import {validateResourceManifest} from './resource-manifest.mjs';
const scalar=s=>typeof s==='string' && !/[\uD800-\uDFFF]/u.test(s);
const token="[a-z0-9!#$%&'*+.^_`{|}~-]+";
const mediaType=new RegExp(`^${token}/${token}$`);
// Authenticates nothing. These entries must be inside the enclosing event.
export function validateAttachments(entries,manifest) {
 if(!Array.isArray(entries) || validateResourceManifest(manifest).state!=='shape-valid')return false;
 const available=new Set(manifest.map(r=>r.id)),used=new Set();
 for(const entry of entries) {
  if(!entry || typeof entry!=='object' || Array.isArray(entry) ||
     Object.keys(entry).sort().join(',')!=='description,mediaType,name,resource' ||
     !available.has(entry.resource) || used.has(entry.resource) ||
     !scalar(entry.name) || !scalar(entry.description) ||
     typeof entry.mediaType!=='string' || !mediaType.test(entry.mediaType))return false;
  used.add(entry.resource);
 }
 return true;
}
