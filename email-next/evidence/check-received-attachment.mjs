import {isPrincipalId} from './principal-identifiers.mjs';
import {validateEnvelopeShape} from './event-envelope.mjs';
import {bindResource,inspectResourceInventory} from './resource-binding.mjs';
import {projectReadable} from './readable-projection.mjs';
let input='';for await(const chunk of process.stdin)input+=chunk;
const fixture=JSON.parse(input);
const principal=isPrincipalId;
const event=fixture.event;
if(!validateEnvelopeShape(event,principal) || !['attachment-message','rich-message'].includes(event.operation.kind)) {
 process.stdout.write(JSON.stringify({state:'invalid-schema'}));
} else {
 const parts=fixture.parts.map(p=>({contentId:p.contentId,bytes:new Uint8Array(Buffer.from(p.base64,'base64'))}));
 const inventory=inspectResourceInventory(event.event,event.operation.manifest,parts);
 const resources=event.operation.attachments.map(a=>({id:a.resource,state:bindResource(event.event,event.operation.manifest,a.resource,parts,fixture.limits).state}));
 const projection=projectReadable(event,()=>({state:'pending'}),principal);
 process.stdout.write(JSON.stringify({state:'validated-unverified',inventory,resources,projection}));
}
