import {isEventReference} from './event-identifiers.mjs';

export function validateMessageShape(value, isPrincipal) {
  if (!value || typeof value !== 'object' || Array.isArray(value) ||
      Object.keys(value).length !== 3 ||
      !['kind','text','replyTo'].every(k => Object.hasOwn(value,k)) ||
      value.kind !== 'message' || typeof value.text !== 'string') return false;
  for (const char of value.text) {
    const n=char.codePointAt(0);
    if (n>=0xd800 && n<=0xdfff) return false;
  }
  return Array.isArray(value.replyTo) && value.replyTo.length<=1 &&
    value.replyTo.every(ref=>isEventReference(ref,isPrincipal));
}

// Caller resolves already authenticated records. No fetching or authority inference.
export function resolveMessageReply(envelope, resolve) {
  const refs=envelope.operation.replyTo;
  if (refs.length===0) return {state:'no-target'};
  const ref=refs[0];
  if (ref.conversation!==envelope.conversation) return {state:'invalid'};
  const result=resolve(ref);
  if (!result || result.state==='pending') return {state:'pending'};
  if (result.state==='conflict') return {state:'conflict'};
  if (result.state!=='valid') return {state:'invalid'};
  const target=result.event;
  if (!target || target.principal!==ref.principal || target.event!==ref.event ||
      target.conversation!==ref.conversation) return {state:'invalid'};
  return {state:'target-matched'};
}
