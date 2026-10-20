import {validateOperationShape} from './form-operations.mjs';
const same=(a,b)=>a && b && a.principal===b.principal && a.event===b.event && a.conversation===b.conversation;
// Resolver records use id, as in submission-target. Caller establishes authentication.
export function validateWithdrawalTargets(event, resolve, isPrincipal) {
  const op=event.operation;
  if (!validateOperationShape(op,isPrincipal) || op.kind!=='withdraw' ||
      op.revision.conversation!==event.conversation ||
      op.submissions.some(r=>r.conversation!==event.conversation || r.principal!==event.principal)) return {state:'invalid'};
  const states=[];
  function get(ref) {
    const result=resolve(ref);
    if (!result || !['valid','pending','conflict','invalid'].includes(result.state)) {states.push('invalid');return;}
    if(result.state!=='valid') {states.push(result.state);return;}
    const e=result.event;
    if(!e || e.id!==ref.event || e.principal!==ref.principal || e.conversation!==ref.conversation ||
        !validateOperationShape(e.operation,isPrincipal)) {states.push('invalid');return;}
    return e;
  }
  const revision=get(op.revision);
  if(revision && (revision.operation.kind!=='form' || revision.operation.form!==op.form)) states.push('invalid');
  for(const ref of op.submissions) {
    const target=get(ref);
    if(target && (target.operation.kind!=='submit' || target.operation.form!==op.form ||
        !same(target.operation.revision,op.revision))) states.push('invalid');
  }
  // All targets inspected: outcome does not depend on set ordering.
  for(const state of ['invalid','conflict','pending']) if(states.includes(state)) return {state};
  return {state:'targets-matched',revision:revision.operation};
}
