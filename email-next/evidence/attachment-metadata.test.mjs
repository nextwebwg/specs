import test from 'node:test';
import assert from 'node:assert/strict';
import {validateAttachments} from './attachment-metadata.mjs';
const resource='1'.repeat(32);
const manifest=[{id:resource,size:'0',sha256:'a'.repeat(64)}];
const entry={resource,name:'report.pdf',description:'Quarterly report',mediaType:'application/pdf'};
test('attachments reference exact manifest entries',()=>{
 assert.equal(validateAttachments([entry],manifest),true);
 assert.equal(validateAttachments([{...entry,resource:'2'.repeat(32)}],manifest),false);
 assert.equal(validateAttachments([entry,entry],manifest),false);
});
test('media type is a bare lowercase type without parameters',()=>{
 for(const mediaType of ['Text/Plain','text/plain;charset=utf-8','text','text/','text/plain\n','text /plain'])assert.equal(validateAttachments([{...entry,mediaType}],manifest),false);
 assert.equal(validateAttachments([{...entry,mediaType:'application/vnd.example+json'}],manifest),true);
});
test('display strings preserve scalar text without interpreting paths',()=>{
 assert.equal(validateAttachments([{...entry,name:'../../a<script>😀',description:''}],manifest),true);
 for(const name of ['\ud800','\udfff'])assert.equal(validateAttachments([{...entry,name}],manifest),false);
});
test('unknown and missing metadata fail shape validation',()=>{
 assert.equal(validateAttachments([{...entry,url:'https://example.test/'}],manifest),false);
 const {description,...missing}=entry;assert.equal(validateAttachments([missing],manifest),false);
 assert.equal(validateAttachments([],manifest),true);
});
