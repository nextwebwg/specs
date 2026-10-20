// RFC1870 accounting experiment. Inputs are a final CRLF-encoded message and one parsed SIZE advertisement.
export function parseSizeAdvertisement(parameter) {
  if (parameter === undefined) return {kind:'unknown'};
  if (typeof parameter !== 'string' || !/^[0-9]+$/.test(parameter)) throw new Error('Invalid SIZE advertisement');
  const maximum = BigInt(parameter);
  return maximum === 0n ? {kind:'unbounded-fixed-limit'} : {kind:'fixed',maximum};
}
export function sizeDeclaration(message) {
  if (!(message instanceof Uint8Array)) throw new TypeError('Expected message octets');
  const bytes = Buffer.from(message);
  if (bytes.length < 2 || bytes.at(-2)!==13 || bytes.at(-1)!==10) throw new Error('Fixture requires final CRLF before DATA terminator');
  for(let i=0;i<bytes.length;i++) {
    if(bytes[i]===10 && (i===0 || bytes[i-1]!==13)) throw new Error('Bare LF');
    if(bytes[i]===13 && bytes[i+1]!==10) throw new Error('Bare CR');
  }
  const size = BigInt(bytes.length);
  if(size.toString().length>20) throw new Error('SIZE value exceeds RFC1870 grammar');
  return size;
}
export function stuffData(message) {
  sizeDeclaration(message);
  const out=[];
  for(let i=0;i<message.length;i++) {
    if(message[i]===46 && (i===0 || message[i-1]===10)) out.push(46);
    out.push(message[i]);
  }
  return Buffer.from([...out,46,13,10]);
}
export function exceedsAdvertisedLimit(message, parameter) {
  const size=sizeDeclaration(message), limit=parseSizeAdvertisement(parameter);
  return limit.kind==='fixed' ? size>limit.maximum : false;
}
