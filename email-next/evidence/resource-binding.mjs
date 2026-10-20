import {isObjectId} from './event-identifiers.mjs';
import {validateResourceManifest,resourceExpectation} from './resource-manifest.mjs';
import {assembleResource} from './resource-assembly.mjs';

export function resourceContentId(event,id) {
  if(!isObjectId(event) || !isObjectId(id)) throw new TypeError('invalid resource identity');
  return `${id}.${event}@resources.email-next.invalid`;
}

// parts are already MIME-parsed and transfer-decoded within ONE selected compound.
// manifest/enclosing identity must already be authenticated by the caller.
export function bindResource(event,manifest,id,parts,limits) {
  if(!isObjectId(event) || validateResourceManifest(manifest).state!=='shape-valid' ||
     !isObjectId(id) || !Array.isArray(parts)) return {state:'invalid'};
  const bounded=resourceExpectation(manifest,id,limits?.maxBytes);
  if(bounded.state!=='bounded') return bounded;
  const cid=resourceContentId(event,id);
  const candidates=parts.filter(part=>part?.contentId===cid);
  if(candidates.length===0) return {state:'missing'};
  if(candidates.length!==1) return {state:'ambiguous'};
  const bytes=candidates[0].bytes;
  if(!(bytes instanceof Uint8Array)) return {state:'invalid'};
  return assembleResource(bounded.expected,[{offset:0,bytes}],limits);
}

// Inventory diagnostics do not authenticate parts or release their bytes.
export function inspectResourceInventory(event,manifest,parts) {
  if(!isObjectId(event) || validateResourceManifest(manifest).state!=='shape-valid' ||
     !Array.isArray(parts) || parts.some(p=>!p || typeof p.contentId!=='string'))return {state:'invalid'};
  const expected=new Map(manifest.map(item=>[resourceContentId(event,item.id),item.id]));
  const counts=new Map(),unbound=[];
  for(const [index,part] of parts.entries()) {
    if(!expected.has(part.contentId))unbound.push(index);
    else counts.set(part.contentId,(counts.get(part.contentId)??0)+1);
  }
  const missing=[],ambiguous=[];
  for(const [cid,id] of expected) {
    const count=counts.get(cid)??0;
    if(count===0)missing.push(id);
    else if(count>1)ambiguous.push(id);
  }
  return {state:missing.length||ambiguous.length||unbound.length?'incomplete-inventory':'matched-inventory',missing,ambiguous,unbound};
}
