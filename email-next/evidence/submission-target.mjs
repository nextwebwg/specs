import {validateOperationShape} from './form-operations.mjs';
import {validateAnswers} from './form-values.mjs';

// Resolver states are trusted outputs of prior authentication and revision-graph checks.
// This function performs no fetching, signature verification, or mutation.
export function validateSubmissionTarget(event, resolve, isPrincipal) {
  const operation=event.operation;
  if (!validateOperationShape(operation,isPrincipal) || operation.kind!=='submit')
    return {state:'invalid',reason:'operation-shape'};
  const reference=operation.revision;
  if (reference.conversation!==event.conversation)
    return {state:'invalid',reason:'cross-conversation'};
  const resolved=resolve(reference);
  if (!resolved || !['valid','pending','conflict','invalid'].includes(resolved.state))
    return {state:'invalid',reason:'resolver-contract'};
  if (resolved.state!=='valid') return {state:resolved.state,reason:'revision-'+resolved.state};
  const revision=resolved.event;
  if (!revision || revision.principal!==reference.principal || revision.id!==reference.event ||
      revision.conversation!==reference.conversation)
    return {state:'invalid',reason:'reference-mismatch'};
  if (!validateOperationShape(revision.operation,isPrincipal) || revision.operation.kind!=='form' ||
      revision.operation.form!==operation.form)
    return {state:'invalid',reason:'wrong-form'};
  if (!validateAnswers(operation.answers,revision.operation.fields))
    return {state:'invalid',reason:'answer-values'};
  // Supersession and author authority are deliberately not accepted by this stage.
  return {state:'target-valid',revision:reference};
}
