// Client-owned rendering of trusted acceptance output. Never parse sender HTML.
export function mountPresentation(root,value){
 root.replaceChildren();const document=root.ownerDocument;
 const text=(tag,value)=>{const e=document.createElement(tag);e.textContent=value;return e;};
 root.append(text('p',value.notice));
 if(value.state==='authenticated-presentation'){
  root.append(text('h2',value.subject||'No subject'));
  const dl=document.createElement('dl');
  for(const [label,content] of [['Author',value.authorPrincipal],['To',value.to.join(', ')],['Cc',value.cc.join(', ')],['Author-stated date',value.authoredAt.display]])dl.append(text('dt',label),text('dd',content||'None'));
  root.append(dl);
  if(value.authoredAt.display==='Unavailable')root.append(text('p','Original author-stated seconds: '+value.authoredAt.source));
 }
 const details=document.createElement('details');details.append(text('summary','Unprotected transport details'));
 for(const [name,values]of Object.entries(value.transport.fields))details.append(text('p',name+': '+values.join(' | ')));
 root.append(details);
}
