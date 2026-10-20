import {isEventReference} from './event-identifiers.mjs';
import {validateMessageShape} from './message-operation.mjs';
import {resolveEditTargets, validateEditShape} from './edit-operation.mjs';
const key = r => JSON.stringify([r.principal,r.conversation,r.event]);
// Reject impossible authority edges before asking the resolver for that history.
const hasLocalScope = event => [event.operation.root,...event.operation.predecessors].every(ref =>
  ref.principal===event.principal && ref.conversation===event.conversation && ref.event!==event.event);

// Iterative synchronous snapshot evaluator. Resolver supplies authentication
// and exact-byte conflict results, not graph validity. Never fetches or writes.
export function evaluateEdit(root, candidates, resolve, isPrincipal, {maxRecords=Infinity, maxReferences=Infinity}={}) {
  if (!isEventReference(root,isPrincipal) || !Array.isArray(candidates) ||
      !candidates.every(r=>isEventReference(r,isPrincipal)))
    throw new TypeError('Expected exact event references');
  for(const limit of [maxRecords,maxReferences])
    if(limit!==Infinity && (!Number.isSafeInteger(limit) || limit<0)) throw new TypeError('Invalid local work budget');
  // Exhaustion returns no candidate view: callers must not publish a prefix.
  if(candidates.length+1>maxReferences) return {state:'incomplete',reason:'reference-budget'};
  let references=candidates.length+1;
  const refs=new Map([[key(root),root],...candidates.map(r=>[key(r),r])]);
  // Include ancestors: a pending child must not conceal a known valid predecessor.
  if(refs.size>maxRecords) return {state:'incomplete',reason:'record-budget'};
  const queue=[...refs.values()];
  const records=new Map();
  for(let i=0;i<queue.length;i++) {
    const found=resolve(queue[i]);
    records.set(key(queue[i]),found);
    if (found?.state!=='valid' || !found.event || key(found.event)!==key(queue[i]) ||
        !validateEditShape(found.event.operation,isPrincipal) || key(found.event.operation.root)!==key(root) ||
        !hasLocalScope(found.event)) continue;
    references+=found.event.operation.predecessors.length+1;
    if(references>maxReferences) return {state:'incomplete',reason:'reference-budget'};
    for(const ref of found.event.operation.predecessors) if(!refs.has(key(ref))) {
      if(refs.size>=maxRecords) return {state:'incomplete',reason:'record-budget'};
      refs.set(key(ref),ref);queue.push(ref);
    }
  }
  const states=new Map(), dependencies=new Map(), dependents=new Map();
  for(const ref of refs.values()) {
    const id=key(ref), found=records.get(id);
    if(!found || found.state==='pending') states.set(id,{state:'pending'});
    else if(found.state==='conflict') states.set(id,{state:'conflict'});
    else if(found.state!=='valid' || !found.event || key(found.event)!==id)
      states.set(id,{state:'invalid'});
    else if(id===key(root)) states.set(id,validateMessageShape(found.event.operation,isPrincipal)
      ? {state:'valid',event:found.event} : {state:'invalid'});
    else if(!validateEditShape(found.event.operation,isPrincipal) || key(found.event.operation.root)!==key(root) ||
            !hasLocalScope(found.event))
      states.set(id,{state:'invalid'});
    else {
      const deps=new Set([key(root),...found.event.operation.predecessors.map(key)]);
      dependencies.set(id,deps);
      for(const dependency of deps) {
        if(!dependents.has(dependency)) dependents.set(dependency,[]);
        dependents.get(dependency).push(id);
      }
    }
  }
  // Kahn traversal resolves each node once. Any remainder is a cycle or depends
  // on one, so invalid dominates unresolved/pending branches for that remainder.
  const ready=[...states.keys()];
  for(let i=0;i<ready.length;i++) for(const id of dependents.get(ready[i])??[]) {
    const deps=dependencies.get(id);deps.delete(ready[i]);
    if(deps.size!==0) continue;
    const event=records.get(id).event;
    const checked=resolveEditTargets(event,ref=>states.get(key(ref)),isPrincipal);
    states.set(id,checked.state==='target-matched'?{state:'valid',event}:checked);
    ready.push(id);
  }
  for(const id of dependencies.keys()) if(!states.has(id)) states.set(id,{state:'invalid'});
  const results=[...refs.values()].map(ref=>({ref,...states.get(key(ref))}));
  const hidden=new Set();
  for(const result of results) if(result.state==='valid' && result.event.operation.kind==='edit')
    for(const ref of result.event.operation.predecessors) hidden.add(key(ref));
  return {state:'evaluated',results, heads:results.filter(r=>r.state==='valid' && !hidden.has(key(r.ref))).map(r=>r.ref)};
}
