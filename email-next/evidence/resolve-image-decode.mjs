// Trusted local adapter; caller authenticates manifest/event and scopes MIME parts.
import {readFileSync} from 'node:fs';
import {resolveImageCandidate} from './image-resource.mjs';
import {resourceContentId} from './resource-binding.mjs';
const {candidate,event,manifest,parts,limits}=JSON.parse(readFileSync(0,'utf8'));
const decoded=parts.map(p=>({...p,bytes:Buffer.from(p.bytes,'base64')}));
const result=resolveImageCandidate(candidate,event,manifest,decoded,limits);
if(result.state!=='encoded-resource')process.stdout.write(JSON.stringify(result));
else {
 const part=decoded.find(p=>p.contentId===resourceContentId(event,result.id));
 const bytes=Buffer.from(result.bytes);
 const type=part.mediaType;
 const png=bytes.length>=8 && bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]));
 const jpeg=bytes.length>=3 && bytes[0]===255 && bytes[1]===216 && bytes[2]===255;
 if(!['image/png','image/jpeg'].includes(type))process.stdout.write(JSON.stringify({state:'unsupported-media-type'}));
 else if((type==='image/png'&&!png)||(type==='image/jpeg'&&!jpeg))process.stdout.write(JSON.stringify({state:'media-type-mismatch'}));
 else process.stdout.write(JSON.stringify({state:'bound-image-candidate',mediaType:type,bytes:bytes.toString('base64')}));
}
