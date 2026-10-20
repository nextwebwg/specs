// Narrow decoded-source scanner. Offsets are half-open UTF-16 code units.
// These ranges precede entity/CRLF interpretation; never derive them from a DOM.
const named={amp:'&',lt:'<',gt:'>',quot:'"',apos:"'"};
const scalar=n=>n>0&&n<=0x10ffff&&!(n>=0xd800&&n<=0xdfff)&&!(n<32&&![9,10,13].includes(n))&&!(n>=127&&n<=159)&&!(n>=0xfdd0&&n<=0xfdef)&&(n&0xffff)!==0xfffe&&(n&0xffff)!==0xffff;
function textValue(raw){
 let out='';
 for(let i=0;i<raw.length;){
  if(raw[i]==='&'){
   const match=/^&(#x[0-9a-fA-F]+|#[0-9]+|amp|lt|gt|quot|apos);/.exec(raw.slice(i));if(!match)throw Error('unsupported-reference');
   const token=match[1];let value=named[token];
   if(value===undefined){const n=token.startsWith('#x')?Number.parseInt(token.slice(2),16):Number(token.slice(1));if(!scalar(n))throw Error('unsupported-reference');value=String.fromCodePoint(n);}
   out+=value;i+=match[0].length;
  }else{
   const n=raw.codePointAt(i);if(!scalar(n)||raw[i]==='<')throw Error('unsupported-text');
   if(raw[i]==='\r'){out+='\n';i+=raw[i+1]==='\n'?2:1;}else{out+=String.fromCodePoint(n);i+=n>0xffff?2:1;}
  }
 }
 return out;
}
export function scanHtmlQuotes(source){
 if(typeof source!=='string')throw TypeError('Decoded HTML string required');
 let at=0;const token=(kind,start,end,extra={})=>({kind,start,end,...extra});
 function opening(tag,allowed){
  const match=new RegExp(`^<${tag}((?:[^"'<>]|"[^"<>]*"|'[^'<>]*')*)>`).exec(source.slice(at));
  if(!match)throw Error('unsupported-opening');
  let rest=match[1];const seen=new Set();
  while(rest.trim()){
   const attr=/^\s+([a-z]+)\s*=\s*(?:"([^"<>]*)"|'([^'<>]*)')/.exec(rest);
   if(!attr||!allowed.includes(attr[1])||seen.has(attr[1]))throw Error('unsupported-attribute');
   seen.add(attr[1]);rest=rest.slice(attr[0].length);
  }
  return match[0].length;
 }
 function paragraph(tag='p',length=3){
  const start=at;at+=length;const parts=[];
  while(!source.startsWith('</'+tag+'>',at)){
   if(at>=source.length)throw Error('unclosed-paragraph');
   const begin=at;
   if(source.startsWith('<br>',at)){at+=4;parts.push(token('br',begin,at,{text:'\n'}));continue;}
   const next=source.indexOf('<',at);at=next===-1?source.length:next;
   if(at===begin)throw Error('unsupported-paragraph-markup');
   parts.push(token('text',begin,at,{text:textValue(source.slice(begin,at))}));
  }
  at+=tag.length+3;return token('paragraph',start,at,{parts,text:parts.map(p=>p.text).join('')});
 }
 function sequence(inQuote,closing=null){
  const nodes=[];
  while(at<source.length){
   if(closing&&source.startsWith('</'+closing+'>',at))return nodes;
   const start=at,space=/^[ \t\r\n]+/.exec(source.slice(at));
   if(space){at+=space[0].length;nodes.push(token('whitespace',start,at,{text:space[0].replace(/\r\n?/g,'\n')}));}
   else if(source.startsWith('<p>',at))nodes.push(paragraph());
   else if(/^<div(?:[ \t\r\n>])/.test(source.slice(at))){
    const length=opening('div',['class']);const body=source.slice(at+length);
    if(/^(?:[^<]|<br>)*<\/div>/.test(body)){nodes.push(paragraph('div',length));continue;}
    at+=length;nodes.push(token('whitespace',start,at,{text:''}));nodes.push(...sequence(inQuote,'div'));
    if(!source.startsWith('</div>',at))throw Error('unclosed-wrapper');const end=at;at+=6;nodes.push(token('whitespace',end,at,{text:''}));
   }
   else if(!inQuote&&/^<blockquote(?:[ \t\r\n>])/.test(source.slice(at))){
    at+=opening('blockquote',['cite','type','class']);const children=sequence(true,'blockquote');if(!source.startsWith('</blockquote>',at))throw Error('unclosed-quote');at+=13;nodes.push(token('quote',start,at,{children}));
   }else throw Error('unsupported-structure');
  }
  if(closing)throw Error('unclosed-container');return nodes;
 }
 try{return {state:'mapped',profile:'strict-paragraph-quote-0',offsetUnit:'utf16-code-unit',source,nodes:sequence(false)};}
 catch(error){return {state:'visible-source',profile:'strict-paragraph-quote-0',offsetUnit:'utf16-code-unit',source,nodes:[token('source',0,source.length,{text:source})],reason:error.message};}
}
export function reconstructHtmlQuotes(source,parents){
 const parsed=scanHtmlQuotes(source);if(parsed.state!=='mapped')return parsed;
 const runs=[];
 for(const parent of parents){const p=scanHtmlQuotes(parent.html);if(p.state!=='mapped')continue;let run=[];
  const flush=()=>{if(run.length)runs.push({message:parent.id,paragraphs:run});run=[];};
  for(const n of p.nodes){if(n.kind==='paragraph')run.push(n);else if(n.kind!=='whitespace')flush();}flush();
 }
 return {...parsed,nodes:parsed.nodes.map(n=>{
  if(n.kind!=='quote')return {...n,presentation:'visible'};
  const quoted=n.children.filter(c=>c.kind==='paragraph');const matches=[];
  if(quoted.some(p=>p.text.trim()))for(const run of runs)for(let i=0;i+quoted.length<=run.paragraphs.length;i++){
   if(quoted.every((p,k)=>p.text===run.paragraphs[i+k].text))matches.push({message:run.message,start:run.paragraphs[i].start,end:run.paragraphs[i+quoted.length-1].end,offsetUnit:'utf16-code-unit'});
  }
  return {...n,presentation:matches.length===1?'repeated-quote':'visible',matchedSource:matches.length===1?matches[0]:null};
 })};
}
