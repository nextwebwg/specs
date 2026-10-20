// A parsed destination is data for a client-owned confirmation/navigation handler.
// This function never fetches, opens, preloads, or assigns a browser target.
export function validateNavigationUrl(value) {
 if(typeof value!=='string' || !/^https?:\/\//i.test(value) ||
    /[\u0000-\u0020\u007f\\]/u.test(value))return {state:'rejected'};
 for(const char of value) {
  const cp=char.codePointAt(0);if(cp>=0xd800 && cp<=0xdfff)return {state:'rejected'};
 }
 // Reject even empty userinfo rather than letting parser normalization erase it.
 const authority=value.slice(value.indexOf('://')+3).split(/[/?#]/,1)[0];
 if(!authority || authority.includes('@'))return {state:'rejected'};
 // URL Standard IPv4-in-IPv6 parsing rejects a decimal piece with leading
 // zeros. Some browser parsers accept it; enforce this before normalization.
 if(authority.startsWith('[')){
  const end=authority.indexOf(']');
  const literal=end<0?'':authority.slice(1,end);
  const tail=literal.slice(literal.lastIndexOf(':')+1);
  if(tail.includes('.')&&tail.split('.').some(piece=>/^0[0-9]+$/.test(piece)))return {state:'rejected'};
 }
 let url;
 try {url=new URL(value);} catch {return {state:'rejected'};}
 if(!['https:','http:'].includes(url.protocol) || !url.hostname || url.username || url.password)return {state:'rejected'};
 return {state:'destination',href:url.href,origin:url.origin};
}
