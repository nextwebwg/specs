import test from 'node:test';import assert from 'node:assert/strict';
import {validateRichMessage} from './rich-message-operation.mjs';
import {validateConversationContext} from './conversation-context.mjs';
const principal='enp0:'+'a'.repeat(64),id='b'.repeat(32);
const base={kind:'rich-message',text:'A blue diagram',html:'<p>A blue diagram</p>',presentation:'html-css-v0',replyTo:[],manifest:[],embedded:[],attachments:[]};
const valid=value=>validateRichMessage(value,p=>p===principal);
test('exact rich body, full inventory and disjoint role schema',()=>{
 assert.equal(valid(base),true);
 const rich={...base,manifest:[{id,size:'1',sha256:'c'.repeat(64)}],embedded:[{resource:id,mediaType:'image/png'}]};
 assert.equal(valid(rich),true);
 for(const changed of [{...base,extra:true},{...base,presentation:'unknown'},{...rich,embedded:[]},{...rich,embedded:[{resource:id,mediaType:'image/svg+xml'}]},{...rich,attachments:[{resource:id,name:'image',description:'',mediaType:'image/png'}]}])assert.equal(valid(changed),false);
});
test('context4 exact rich agreement, older context cannot infer support',()=>{
 const application={envelopeVersion:'1',payload:'mime-rich-v0',operations:['rich-message']};
 const context={version:'4',purpose:'conversation-context',conversation:'d'.repeat(32),profile:'mls-1-0001',administrators:[principal],application,ordering:{kind:'fixed-roster-v0'}};
 assert.equal(validateConversationContext(context,{configuredApplication:application}),true);
 assert.equal(validateConversationContext({...context,version:'3'},{configuredApplication:application}),false);
 assert.equal(validateConversationContext(context,{configuredApplication:{...application,payload:'mime-contribution-v0'}}),false);
});
