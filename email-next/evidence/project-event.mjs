import {isPrincipalId} from './principal-identifiers.mjs';
import {projectReadable} from './readable-projection.mjs';
let input='';for await(const chunk of process.stdin)input+=chunk;
const result=projectReadable(JSON.parse(input),()=>({state:'pending'}),isPrincipalId);
process.stdout.write(JSON.stringify(result));
