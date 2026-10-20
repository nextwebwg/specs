import {bindResource} from './resource-binding.mjs';
let input='';
for await(const chunk of process.stdin)input+=chunk;
const fixture=JSON.parse(input);
const parts=fixture.parts.map(p=>({contentId:p.contentId,bytes:new Uint8Array(Buffer.from(p.base64,'base64'))}));
const result=bindResource(fixture.event,fixture.manifest,fixture.id,parts,fixture.limits);
process.stdout.write(JSON.stringify({state:result.state}));
