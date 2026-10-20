import {randomBytes} from 'node:crypto';
export function isObjectId(value) {
  return typeof value === 'string' && /^[0-9a-f]{32}$/.test(value) && value !== '0'.repeat(32);
}
export function newObjectId() {
  let value;
  do {value=randomBytes(16).toString('hex');} while (!isObjectId(value));
  return value;
}
// Principal validation remains an explicit security-profile responsibility.
// This checks a parsed object; duplicate JSON members must be rejected before parsing it.
export function isEventReference(value, isPrincipal) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false;
  const keys=Object.keys(value).sort();
  return keys.length===3 && keys[0]==='conversation' && keys[1]==='event' && keys[2]==='principal' &&
    isObjectId(value.event) && isObjectId(value.conversation) &&
    typeof value.principal==='string' && isPrincipal(value.principal) === true;
}
