import {test} from 'node:test';
import assert from 'node:assert/strict';
import {validateHostedHolderObservation as valid} from './hosted-holder-operation.mjs';
const principal=value=>value==='enp0:'+'a'.repeat(64);
const op={kind:'hosted-holder-observation',text:'Reply',target:{principal:'enp0:'+'a'.repeat(64),conversation:'1'.repeat(32),event:'2'.repeat(32)},service:'https://host.example',attribution:'grant-holder'};
test('exact holder observation has no mailbox-authority substitution',()=>{
  assert.equal(valid(op,principal),true);
  for(const change of [{attribution:'verified-mailbox'},{text:'  '},{text:'\ud800'},{service:'http://host.example'},{principal:'enp0:'+'a'.repeat(64)},{target:{...op.target,event:'0'.repeat(32)}}]) assert.equal(valid({...op,...change},principal),false);
});
