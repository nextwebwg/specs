import {verifyPassiveDiscovery,verifyApplicationDiscovery,verifyTupleDiscovery,verifyRichDiscovery,verifyPrivateCopyDiscovery,verifyPresentationDiscovery,verifyQuorumDiscovery,verifyQuorumExchangeDiscovery} from './binding-signature.mjs';
let text='';for await(const chunk of process.stdin)text+=chunk;
const request=JSON.parse(text);
const verifier=request.version==='7'?verifyQuorumExchangeDiscovery:request.version==='6'?verifyQuorumDiscovery:request.version==='5'?verifyPresentationDiscovery:request.version==='4'?verifyPrivateCopyDiscovery:request.version==='3'?verifyRichDiscovery:request.version==='2'?verifyTupleDiscovery:request.version==='1'?verifyApplicationDiscovery:(request.version===undefined||request.version==='0')?verifyPassiveDiscovery:null;
process.stdout.write(JSON.stringify({status:verifier?verifier(Buffer.from(request.payload,'base64'),request.signature,request.key):'invalid-proof'}));
