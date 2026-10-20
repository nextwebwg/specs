import {validatePresentation} from './managed-presentation.mjs';
import {validateRichMessage} from './rich-message-operation.mjs';
import {validateHostedHolderObservation} from './hosted-holder-operation.mjs';
import {validateReactionOperation} from './reaction-operations.mjs';
import {isServiceOrigin,validateServiceQuestionBinding} from './service-question.mjs';
import {validateButtonOperation} from './button-operations.mjs';
import {validateEditShape} from './edit-operation.mjs';
import {validateAttachmentMessage} from './attachment-operation.mjs';
import {isObjectId} from './event-identifiers.mjs';
import {validateMessageShape} from './message-operation.mjs';
import {validateOperationShape} from './form-operations.mjs';

function principalSet(value, isPrincipal) {
  return Array.isArray(value) && value.length > 0 &&
    value.every(p => typeof p === 'string' && isPrincipal(p) === true) &&
    new Set(value).size === value.length;
}

// These describe the author's intended disclosure, not proof against later copying.
export function validateDisclosures(value, version = '1') {
  if (!Array.isArray(value)) return false;
  let previous = '', plaintext = false, separate = false;
  for (const item of value) {
    if (!item || typeof item !== 'object' || Array.isArray(item)) return false;
    if (item.kind === 'separate-protected-copy') {
      if(!['2','3'].includes(version)||Object.keys(item).length!==1||separate||plaintext||previous)return false;
      separate=true;
    } else if (item.kind === 'plaintext-email') {
      if (Object.keys(item).length !== 1 || plaintext || previous) return false;
      plaintext = true;
    } else if (item.kind === 'provider-hosted') {
      if (Object.keys(item).length !== 3 || !Object.hasOwn(item,'service') ||
          item.model !== 'bearer' || !isServiceOrigin(item.service) ||
          (previous && previous >= item.service)) return false;
      previous = item.service;
    } else return false;
  }
  return true;
}

// Input must already pass strict byte decoding. This does not authenticate anything.
export function validateEnvelopeShape(value, isPrincipal) {
  const keys=['version','purpose','event','conversation','principal','audience','operation'];
  if (['1','2','3'].includes(value?.version)) keys.push('disclosures');
  if(value?.version==='3')keys.push('presentation');
  return value !== null && typeof value === 'object' && !Array.isArray(value) &&
    Object.keys(value).length === keys.length && keys.every(k => Object.hasOwn(value,k)) &&
    (value.version === '0' || (['1','2','3'].includes(value.version) && validateDisclosures(value.disclosures,value.version))) && value.purpose === 'contribution' &&
    isObjectId(value.event) && isObjectId(value.conversation) &&
    typeof value.principal === 'string' && isPrincipal(value.principal) === true &&
    principalSet(value.audience,isPrincipal) && value.audience.includes(value.principal) &&
    (value.version!=='3'||validatePresentation(value.presentation,value.principal,value.audience,isPrincipal)) &&
    ((['1','2','3'].includes(value.version) && validateRichMessage(value.operation,isPrincipal)) || (['1','2','3'].includes(value.version) && validateHostedHolderObservation(value.operation,isPrincipal)) || validateReactionOperation(value.operation,isPrincipal) || validateServiceQuestionBinding(value,isPrincipal) || validateButtonOperation(value.operation,isPrincipal) || validateEditShape(value.operation,isPrincipal) || validateOperationShape(value.operation,isPrincipal) || validateMessageShape(value.operation,isPrincipal) || validateAttachmentMessage(value.operation,isPrincipal));
}

// Context must come from independently verified protection, never message headers.
// Exact-byte authentication, reference/graph authority and effects remain caller work.
export function checkEnvelopeContext(value, context, isPrincipal) {
  if (!validateEnvelopeShape(value,isPrincipal)) return 'invalid-shape';
  if (!context || context.status !== 'verified') return 'unverified';
  if (context.version !== value.version || context.purpose !== value.purpose ||
      context.conversation !== value.conversation || context.principal !== value.principal ||
      !principalSet(context.audience,isPrincipal) ||
      context.audience.length !== value.audience.length ||
      !context.audience.every(p => value.audience.includes(p))) return 'context-mismatch';
  return 'context-matched';
}
