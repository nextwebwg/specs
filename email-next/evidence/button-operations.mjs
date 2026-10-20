import {isObjectId, isEventReference} from './event-identifiers.mjs';

function exact(value, keys) {
  return value !== null && typeof value === 'object' && !Array.isArray(value) &&
    Object.keys(value).length === keys.length && keys.every(k => Object.hasOwn(value, k));
}
function text(value) {
  return typeof value === 'string' && value.trim().length > 0 &&
    !Array.from(value).some(c => c.codePointAt(0) >= 0xd800 && c.codePointAt(0) <= 0xdfff);
}
const key = ref => JSON.stringify([ref.principal, ref.conversation, ref.event]);

// Candidate operations only: strict JSON decoding and authentication precede use.
export function validateButtonOperation(value, isPrincipal) {
  if (exact(value, ['kind', 'text', 'options']) && value.kind === 'question') {
    return text(value.text) && Array.isArray(value.options) && value.options.length > 0 &&
      value.options.every(o => exact(o, ['id', 'label']) && isObjectId(o.id) && text(o.label)) &&
      new Set(value.options.map(o => o.id)).size === value.options.length;
  }
  return exact(value, ['kind', 'question', 'option', 'replaces']) && value.kind === 'answer' &&
    isEventReference(value.question, isPrincipal) && isObjectId(value.option) &&
    Array.isArray(value.replaces) && value.replaces.every(r => isEventReference(r, isPrincipal)) &&
    new Set(value.replaces.map(key)).size === value.replaces.length;
}

// The caller supplies authenticated, authorized records; this does not discover them.
export function resolveButtonAnswer(envelope, resolve, isPrincipal) {
  const op = envelope.operation;
  if (!validateButtonOperation(op, isPrincipal) || op.kind !== 'answer' ||
      op.question.conversation !== envelope.conversation ||
      op.replaces.some(r => r.conversation !== envelope.conversation ||
        r.principal !== envelope.principal || r.event === envelope.event)) return {state: 'invalid'};
  let pending = false;
  let conflict = false;
  let question;
  for (const [i, ref] of [op.question, ...op.replaces].entries()) {
    const result = resolve(ref);
    if (!result || result.state === 'pending') { pending = true; continue; }
    if (result.state === 'conflict') { conflict = true; continue; }
    const event = result.event;
    if (result.state !== 'valid' || !event || event.principal !== ref.principal ||
        event.event !== ref.event || event.conversation !== ref.conversation ||
        !validateButtonOperation(event.operation, isPrincipal)) return {state: 'invalid'};
    if (i === 0) {
      if (event.operation.kind !== 'question' || !event.operation.options.some(o => o.id === op.option)) return {state: 'invalid'};
      question = event.operation;
    } else if (event.operation.kind !== 'answer' || key(event.operation.question) !== key(op.question)) {
      return {state: 'invalid'};
    }
  }
  if (conflict) return {state: 'conflict'};
  if (pending) return {state: 'pending'};
  return {state: 'references-matched', question: question.text,
    answer: question.options.find(o => o.id === op.option).label};
}
