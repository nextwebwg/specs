// Conservative fixed-line text/plain experiment; not an RFC3676 flowed-text parser.
// The caller supplies already decoded text and explicitly selected earlier messages.
export function reconstructQuotes(text, parents) {
  const lines = text.split(/\r\n|\n|\r/);
  const parsed = lines.map((line, index) => {
    const match = /^(>+)( ?)(.*)$/.exec(line);
    return match ? {index, original:line, depth:match[1].length, text:match[3]} : {index, original:line, depth:0,text:line};
  });
  const blocks=[];
  for(let i=0;i<parsed.length;) {
    const start=i, depth=parsed[i].depth;
    while(i<parsed.length && parsed[i].depth===depth) i++;
    const group=parsed.slice(start,i);
    const candidate=group.map(x=>x.text);
    const matches=[];
    // Only one-level quotes with meaningful text qualify. Preserve nested/ambiguous text.
    if(depth===1 && candidate.some(x=>x.trim().length)) {
      for(const parent of parents) {
        const source=parent.text.split(/\r\n|\n|\r/);
        for(let j=0;j+candidate.length<=source.length;j++) {
          if(candidate.every((line,k)=>line===source[j+k])) matches.push({parent:parent.id,start:j,end:j+candidate.length});
        }
      }
    }
    blocks.push({start,end:i,lines:group.map(x=>x.original),kind:matches.length===1?'repeated-quote':'visible',source:matches.length===1?matches[0]:null});
  }
  return blocks;
}
