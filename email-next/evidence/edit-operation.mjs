import {isEventReference} from './event-identifiers.mjs';
import {validateMessageShape} from './message-operation.mjs';

const key = ref => JSON.stringify([ref.principal, ref.conversation, ref.event]);
export function validateEditShape(value, isPrincipal) {
  if (!value || typeof value !== 'object' || Array.isArray(value) ||
      Object.keys(value).length !== 4 ||
      !['kind', 'root', 'predecessors', 'text'].every(k => Object.hasOwn(value, k)) ||
      value.kind !== 'edit' || !isEventReference(value.root, isPrincipal) ||
      !validateMessageShape({kind:'message', text:value.text, replyTo:[]}, isPrincipal) ||
      !Array.isArray(value.predecessors) || value.predecessors.length === 0 ||
      !value.predecessors.every(ref => isEventReference(ref, isPrincipal))) return false;
  return new Set(value.predecessors.map(key)).size === value.predecessors.length;
}

// Resolver 'valid' means prior authentication AND dependency-graph validation.
// This checks exact targets; it neither establishes that trust nor commits effects.
export function resolveEditTargets(envelope, resolve, isPrincipal) {
  if (!validateEditShape(envelope?.operation, isPrincipal) ||
      !isEventReference({principal:envelope.principal, conversation:envelope.conversation,
        event:envelope.event}, isPrincipal)) return {state:'invalid'};
  const op = envelope.operation;
  const references=[op.root, ...op.predecessors];
  // Scope is knowable without retrieval. Check the entire operation before
  // resolving even its valid-looking prefix (including readable projections).
  if(references.some(ref=>ref.principal!==envelope.principal ||
      ref.conversation!==envelope.conversation || ref.event===envelope.event))
    return {state:'invalid'};
  const states = references.map((ref, index) => {
    const result = resolve(ref);
    if (!result || result.state === 'pending') return 'pending';
    if (result.state === 'conflict') return 'conflict';
    if (result.state !== 'valid' || !result.event || key(result.event) !== key(ref)) return 'invalid';
    const target = result.event.operation;
    if (index === 0 || key(ref) === key(op.root))
      return validateMessageShape(target, isPrincipal) ? 'target-matched' : 'invalid';
    return validateEditShape(target, isPrincipal) && key(target.root) === key(op.root)
      ? 'target-matched' : 'invalid';
  });
  for (const state of ['invalid', 'conflict', 'pending'])
    if (states.includes(state)) return {state};
  return {state:'target-matched'};
}
