import {reconstructHtmlQuotes} from './html-quotes.mjs';
import {reconstructQuotes} from './legacy-quotes.mjs';
import {reconstructFlowedQuotes} from './flowed-quotes.mjs';
const data=await(await fetch('/fixtures.json')).json();
const select=document.querySelector('#scenario'),container=document.querySelector('#messages');
let mode='conversation',included=false,selection=null;const expanded=new Map();
const node=(tag,text)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;return n;};
for(const scenario of data.scenarios){const option=node('option',scenario.title);option.value=scenario.id;select.append(option);}
function scenario(){return data.scenarios.find(s=>s.id===select.value);}
function shown(){const s=scenario();return included&&s.optional?[s.optional,...s.messages]:s.messages;}
function map(message,ids){
 const parents=message.parents.filter(id=>ids.includes(id)).map(id=>data.messages[id]);
 if(message.mediaType==='text/html'){
  const mapped=reconstructHtmlQuotes(message.text,parents.filter(p=>p.mediaType==='text/html').map(p=>({id:p.id,html:p.text})));
  return mapped.nodes.map(n=>({html:n,currentRange:{start:n.start,end:n.end,offsetUnit:'utf16-code-unit'},original:message.text.slice(n.start,n.end),display:n.kind==='quote'?n.children.filter(c=>c.kind==='paragraph').map(c=>c.text).join('\n'):n.text,kind:n.presentation==='repeated-quote'?'repeated-quote':'visible',source:n.matchedSource??null,diagnostics:mapped.state==='visible-source'?[mapped.reason]:[]}));
 }
 if(message.format.toLowerCase()==='flowed')return reconstructFlowedQuotes(message,parents).map(b=>({...b,currentLines:b.sourceLines,original:b.sourceLines.map(i=>message.text.split(/\r\n|\r|\n/)[i]).join('\n'),display:b.paragraphs.map(p=>p.text).join('\n'),diagnostics:b.paragraphs.flatMap(p=>p.diagnostics),source:b.source?{message:b.source.message,lines:b.source.sourceLines}:null}));
 return reconstructQuotes(message.text,parents).map(b=>({...b,currentLines:Array.from({length:b.end-b.start},(_,i)=>b.start+i),original:b.lines.join('\n'),display:b.lines.join('\n'),diagnostics:[],source:b.source?{message:b.source.parent,lines:Array.from({length:b.source.end-b.source.start},(_,i)=>b.source.start+i)}:null}));
}
function renderHtml(n){
 if(n.kind==='source')return node('pre',n.text);
 if(n.kind==='whitespace')return document.createTextNode(n.text);
 if(n.kind==='paragraph'){const p=node('p');for(const part of n.parts)p.append(part.kind==='br'?node('br'):document.createTextNode(part.text));return p;}
 const quote=node('blockquote');for(const child of n.children)quote.append(renderHtml(child));return quote;
}
function focusMessage(id){document.getElementById('message-'+id)?.focus();}
function render(focus){
 const ids=shown();container.replaceChildren();document.querySelector('#include').hidden=!scenario().optional||included;
 document.querySelector('#conversation').setAttribute('aria-pressed',String(mode==='conversation'));document.querySelector('#original').setAttribute('aria-pressed',String(mode==='original'));
 document.querySelector('#status').textContent=mode==='original'?'Original decoded bodies; complete MIME source is available below each message.':'Only unique exact repetitions collapse. Visible text is not assigned a guessed source.';
 window.presentationMaps={};
 for(const id of ids){
  const message=data.messages[id],article=node('article'),heading=node('h2',message.sender);heading.id='message-'+id;heading.tabIndex=-1;article.append(heading,node('p',message.date+' · unverified header'));
  const tools=node('div');tools.className='message-tools';const view=node('button',mode==='original'?'Back to conversation':'View original');view.addEventListener('click',()=>{mode=mode==='original'?'conversation':'original';render(id);});tools.append(view);const download=node('a','Download original .eml');download.href='/messages/'+id+'.eml';download.download=id+'.eml';download.className='download';tools.append(download);article.append(tools);
  if(selection?.message===id){const label=node('p',selection.lines?'Selected source lines (zero-based): '+selection.lines.join(', '):'Selected decoded HTML UTF-16 range: ['+selection.start+', '+selection.end+')');label.className='source-selection';article.append(label);}
  const blocks=map(message,ids);window.presentationMaps[id]=blocks.map(b=>({message:id,profile:message.mediaType==='text/html'?'strict-paragraph-quote-0':message.format,currentLines:b.currentLines,currentRange:b.currentRange,kind:b.kind,source:b.source,diagnostics:b.diagnostics}));
  if(mode==='original'){const body=node('pre',message.text);body.className='original-body';article.append(body);}
  else for(const b of blocks){
   if(b.kind==='repeated-quote'){
    const details=node('details');details.className='quote';const key=id+':'+(b.currentLines?b.currentLines.join(','):b.currentRange.start+'-'+b.currentRange.end);details.open=expanded.get(key)??false;
    const excerpt=b.display.replace(/^> ?/gm,'').trim().slice(0,100);details.append(node('summary','Repeated quotation: '+excerpt+' — inferred source '+b.source.message));
    details.append(b.html?renderHtml(b.html):node('pre',b.original));const source=node('button','Inspect source '+b.source.message);source.addEventListener('click',()=>{selection=b.source;mode='original';render(b.source.message);});details.append(source);
    details.addEventListener('toggle',()=>{if(details.isConnected)expanded.set(key,details.open);});article.append(details);
   }else article.append(b.html?renderHtml(b.html):node('pre',b.display));
   if(b.diagnostics.length)article.append(node('p','Decoding/reflow diagnostics: '+b.diagnostics.join(', ')));
  }
  const source=node('details');source.className='source';source.append(node('summary','MIME source and presentation map'),node('pre',message.original),node('pre',JSON.stringify(window.presentationMaps[id],null,2)));article.append(source);
  if(message.diagnostics.length)article.append(node('p','MIME diagnostics: '+message.diagnostics.join(', ')));
  const missing=message.parents.filter(p=>!ids.includes(p));if(missing.length)article.append(node('p','Unavailable referenced messages: '+missing.join(', ')));
  container.append(article);
 }
 if(focus)focusMessage(focus);
}
select.addEventListener('change',()=>{included=false;selection=null;render();});
for(const target of ['conversation','original'])document.querySelector('#'+target).addEventListener('click',()=>{const id=document.activeElement?.closest('article')?.querySelector('h2')?.id?.slice(8)||shown()[0];mode=target;render(id);});
document.querySelector('#include').addEventListener('click',()=>{const id=scenario().messages[0];included=true;render(id);});render();
