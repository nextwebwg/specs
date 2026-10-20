// Local authenticated-context validator. Agreement is supplied from durable state.
import {readFileSync} from 'node:fs';
import {validateConversationContext} from './conversation-context.mjs';
const {context,application}=JSON.parse(readFileSync(0,'utf8'));
process.stdout.write(validateConversationContext(context,{configuredEndpointOrdering:true,configuredApplication:application})&&context.ordering?.kind==='designated-member-v0'?'valid':'invalid');
