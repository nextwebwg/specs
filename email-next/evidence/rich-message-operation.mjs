// Shape only; HTML conformance and scoped byte availability are separate gates.
import {validateMessageShape} from './message-operation.mjs';
import {validateResourceManifest} from './resource-manifest.mjs';
import {validateAttachments} from './attachment-metadata.mjs';
export function validateRichMessage(value,isPrincipal){
 if(!value || typeof value!=='object' || Array.isArray(value) || Object.keys(value).sort().join(',')!=='attachments,embedded,html,kind,manifest,presentation,replyTo,text' || value.kind!=='rich-message' || value.presentation!=='html-css-v0' || typeof value.html!=='string' || /[\uD800-\uDFFF]/u.test(value.html))return false;
 if(!validateMessageShape({kind:'message',text:value.text,replyTo:value.replyTo},isPrincipal) || validateResourceManifest(value.manifest).state!=='shape-valid' || !validateAttachments(value.attachments,value.manifest) || !Array.isArray(value.embedded))return false;
 const manifest=new Set(value.manifest.map(x=>x.id)),used=new Set(value.attachments.map(x=>x.resource));let previous='';
 for(const item of value.embedded){
  if(!item || typeof item!=='object' || Array.isArray(item) || Object.keys(item).sort().join(',')!=='mediaType,resource' || !manifest.has(item.resource) || used.has(item.resource) || item.resource<=previous || !['image/png','image/jpeg'].includes(item.mediaType))return false;
  used.add(item.resource);previous=item.resource;
 }
 return used.size===manifest.size;
}
