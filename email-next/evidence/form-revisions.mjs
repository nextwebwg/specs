import {validateOperationShape} from './form-operations.mjs';
import {isObjectId} from './event-identifiers.mjs';

// Records have already passed cryptographic authentication and strict decoding.
// octets are the exact authenticated bytes; their binding to operation is a caller invariant.
export function deriveFormRevisions(records, isPrincipal) {
  const key=r=>JSON.stringify([r.principal,r.id]);
  const groups=new Map();
  for(const record of records) {
    if(!isPrincipal(record.principal) || !isObjectId(record.id) || !isObjectId(record.conversation) ||
        !(record.octets instanceof Uint8Array)) throw new TypeError('Authenticated record contract');
    const k=key(record);
    if(!groups.has(k))groups.set(k,new Map());
    groups.get(k).set(Buffer.from(record.octets).toString('base64'),record);
  }
  const events=new Map();
  const conflicts=new Set();
  for(const [k,variants] of groups) {
    if(variants.size===1)events.set(k,[...variants.values()][0]);else conflicts.add(k);
  }
  // Multiple initial definitions under one author/form identity are ambiguous.
  const roots=new Map();
  for(const [k,r] of events) {
    if(validateOperationShape(r.operation,isPrincipal) && r.operation.kind==='form' && r.operation.supersedes.length===0) {
      const scope=JSON.stringify([r.principal,r.operation.form]);
      if(!roots.has(scope))roots.set(scope,[]);
      roots.get(scope).push(k);
    }
  }
  const ambiguousRoots=new Set([...roots.values()].filter(a=>a.length>1).flat());
  function validate(k,path=new Set()) {
    if(conflicts.has(k)||ambiguousRoots.has(k))return {state:'conflict'};
    if(!events.has(k))return {state:'pending'};
    if(path.has(k))return {state:'invalid'};
    const r=events.get(k), op=r.operation;
    if(!validateOperationShape(op,isPrincipal)||op.kind!=='form')return {state:'invalid'};
    const history=new Map();
    let pending=false;
    for(const ref of op.supersedes) {
      if(ref.principal!==r.principal||ref.conversation!==r.conversation||ref.event===r.id)return {state:'invalid'};
      const targetKey=key({principal:ref.principal,id:ref.event});
      const prior=validate(targetKey,new Set(path).add(k));
      if(prior.state==='conflict'||prior.state==='invalid')return {state:'invalid'};
      if(prior.state==='pending'){pending=true;continue;}
      const target=events.get(targetKey);
      if(target.conversation!==ref.conversation||target.operation.form!==op.form)return {state:'invalid'};
      for(const [field,type] of prior.history) {
        if(history.has(field)&&history.get(field)!==type)return {state:'invalid'};
        history.set(field,type);
      }
    }
    if(pending)return {state:'pending'};
    for(const field of op.fields) {
      if(history.has(field.field)&&history.get(field.field)!==field.type)return {state:'invalid'};
      history.set(field.field,field.type);
    }
    return {state:'valid',history};
  }
  const status=new Map();
  for(const k of new Set([...groups.keys()]))status.set(k,validate(k).state);
  const superseded=new Set();
  for(const [k,r] of events)if(status.get(k)==='valid')for(const ref of r.operation.supersedes)
    superseded.add(key({principal:ref.principal,id:ref.event}));
  return {
    status:Object.fromEntries([...status].sort(([a],[b])=>a.localeCompare(b))),
    heads:[...events.keys()].filter(k=>status.get(k)==='valid'&&!superseded.has(k)).sort(),
  };
}
