function parseHostedJSON(source) {
  let index = 0;
  function space() { while (' \t\r\n'.includes(source[index]) && index < source.length) index++; }
  function string() {
    const start = index++;
    let escaped = false;
    while (index < source.length) {
      const character = source[index++];
      if (character === '"' && !escaped) {
        const result = JSON.parse(source.slice(start, index));
        if ([...result].some(character => { const point = character.codePointAt(0); return point >= 0xd800 && point <= 0xdfff; })) throw Error('scalar');
        return result;
      }
      escaped = character === '\\' && !escaped;
    }
    throw Error('string');
  }
  function value(depth) {
    if (depth > 32) throw Error('depth');
    space();
    if (source[index] === '"') return string();
    const object = source[index] === '{';
    if (!object && source[index] !== '[') throw Error('type');
    index++;
    const result = object ? Object.create(null) : [];
    const end = object ? '}' : ']';
    space();
    if (source[index] === end) { index++; return result; }
    while (true) {
      space();
      if (object) {
        if (source[index] !== '"') throw Error('key');
        const key = string();
        if (Object.hasOwn(result, key)) throw Error('duplicate');
        space();
        if (source[index++] !== ':') throw Error('colon');
        result[key] = value(depth + 1);
      } else result.push(value(depth + 1));
      space();
      const next = source[index++];
      if (next === end) return result;
      if (next !== ',') throw Error('separator');
    }
  }
  const result = value(0);
  space();
  if (index !== source.length) throw Error('trailing');
  return result;
}
async function readHostedJSON(response) {
  if (response.headers.get('content-encoding')) throw Error('coding');
  const reader = response.body.getReader();
  const chunks = [];
  let length = 0;
  while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    length += value.length;
    if (length > 1048576) { await reader.cancel(); throw Error('size'); }
    chunks.push(value);
  }
  const bytes = new Uint8Array(length);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
  if (bytes[0] === 239 && bytes[1] === 187 && bytes[2] === 191) throw Error('BOM');
  return parseHostedJSON(new TextDecoder('utf-8', {fatal:true}).decode(bytes));
}
