import {isEventReference} from './event-identifiers.mjs';
import {isServiceOrigin} from './service-question.mjs';

// Shape only. The observer authenticates this operation; the holder is not a principal.
export function validateHostedHolderObservation(value,isPrincipal) {
  if (!value || typeof value!=='object' || Array.isArray(value) ||
      Object.keys(value).length!==5 ||
      !['kind','text','target','service','attribution'].every(k=>Object.hasOwn(value,k)) ||
      value.kind!=='hosted-holder-observation' || value.attribution!=='grant-holder' ||
      typeof value.text!=='string' || !value.text.trim() ||
      !isServiceOrigin(value.service) || !isEventReference(value.target,isPrincipal)) return false;
  for (const char of value.text) {
    const code=char.codePointAt(0);
    if (code>=0xd800 && code<=0xdfff) return false;
  }
  return true;
}
