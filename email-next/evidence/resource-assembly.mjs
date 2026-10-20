import {createHash} from 'node:crypto';

// expected is a trusted fixture, not a parsed or authenticated resource manifest.
// All limits are caller policy, not universal attachment-size or network limits.
export function assembleResource(expected, chunks, limits) {
  if (!limits || !['maxBytes','maxChunks','maxInputBytes'].every(k=>Number.isSafeInteger(limits[k]) && limits[k]>=0) || !expected ||
      !Number.isSafeInteger(expected.size) || expected.size<0 ||
      typeof expected.sha256!=='string' || !/^[0-9a-f]{64}$/.test(expected.sha256) ||
      !Array.isArray(chunks)) return {state:'invalid'};
  if(expected.size>limits.maxBytes || chunks.length>limits.maxChunks) return {state:'limit-exceeded'};
  // Check all ranges before allocating output; do not clamp or truncate.
  let remaining=limits.maxInputBytes;
  for(const chunk of chunks) {
    if(!chunk || !Number.isSafeInteger(chunk.offset) || chunk.offset<0 ||
        !(chunk.bytes instanceof Uint8Array) || chunk.offset>expected.size ||
        chunk.bytes.length>expected.size-chunk.offset) return {state:'invalid'};
    if(chunk.bytes.length>remaining) return {state:'limit-exceeded'};
    remaining-=chunk.bytes.length;
  }
  const bytes=new Uint8Array(expected.size),seen=new Uint8Array(expected.size);
  let count=0;
  for(const chunk of chunks) {
    for(let i=0;i<chunk.bytes.length;i++) {
      const at=chunk.offset+i;
      if(seen[at] && bytes[at]!==chunk.bytes[i]) return {state:'conflict'};
      if(!seen[at]) {seen[at]=1;count++;bytes[at]=chunk.bytes[i];}
    }
  }
  if(count!==expected.size) return {state:'incomplete'};
  const digest=createHash('sha256').update(bytes).digest('hex');
  if(digest!==expected.sha256) return {state:'digest-mismatch'};
  return {state:'complete',bytes};
}
