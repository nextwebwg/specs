import {bindResource} from './resource-binding.mjs';
import {isObjectId} from './event-identifiers.mjs';

// Caller authenticates the HTML, event and manifest together and supplies parts
// from the selected compound only. This releases encoded bytes, never an image.
export function resolveImageCandidate(candidate,event,manifest,parts,limits) {
  if(typeof candidate!=='string' || !isObjectId(event) ||
     !/^cid:/i.test(candidate))return {state:'invalid'};
  let cid;
  try { cid=decodeURIComponent(candidate.slice(4)); }
  catch { return {state:'invalid'}; }
  const match=/^([0-9a-f]{32})\.([0-9a-f]{32})@resources\.email-next\.invalid$/.exec(cid);
  if(!match || match[2]!==event)return {state:'invalid'};
  const result=bindResource(event,manifest,match[1],parts,limits);
  if(result.state!=='complete')return result;
  return {state:'encoded-resource',id:match[1],bytes:result.bytes};
}
