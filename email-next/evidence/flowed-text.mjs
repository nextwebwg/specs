// Display experiment on decoded Unicode text. Never use this output for authentication.
export function interpretPlainText(text, {format='fixed', delsp='no'}={}) {
  const lines=text.split(/\r\n|\n|\r/);
  // A terminal line ending terminates the preceding line; it is not another empty line.
  if (/(?:\r\n|\n|\r)$/.test(text)) lines.pop();
  if (text==='') return [];
  const flowed=String(format).toLowerCase()==='flowed';
  const deleteSpace=String(delsp).toLowerCase()==='yes';
  const result=[];
  let paragraph=null;
  function flush(reason) {
    if(!paragraph)return;
    if(reason)paragraph.diagnostics.push(reason);
    result.push(paragraph);paragraph=null;
  }
  for(let i=0;i<lines.length;i++) {
    const original=lines[i];
    if(!flowed){result.push({text:original,depth:0,sourceLines:[i],kind:'fixed',diagnostics:[]});continue;}
    const prefix=/^>*/.exec(original)[0];
    const depth=prefix.length;
    let content=original.slice(depth);
    if(content.startsWith(' '))content=content.slice(1);
    const signature=content==='-- ';
    const soft=!signature&&content.endsWith(' ');
    if(paragraph&&(paragraph.depth!==depth||signature))flush(signature?'flow-before-signature':'flow-before-depth-change');
    if(signature){result.push({text:content,depth,sourceLines:[i],kind:'signature',diagnostics:[]});continue;}
    if(soft&&deleteSpace)content=content.slice(0,-1);
    if(!paragraph)paragraph={text:'',depth,sourceLines:[],kind:soft?'paragraph':'fixed',diagnostics:[]};
    paragraph.text+=content;
    paragraph.sourceLines.push(i);
    if(!soft)flush();
  }
  flush('flow-at-end');
  return result;
}
