// Pass an absolute file URL to a pinned parse5 installation's dist/index.js.
const {parse}=await import(process.argv[2]);
const cases={
 template:'<table><template><tr><td>hidden</td></tr></template></table><p>visible</p>',
 noscript:'<noscript><p>hidden</p></noscript><p>visible</p>',
 foreign:'<svg><foreignObject><p>hidden</p></foreignObject></svg><p>visible</p>'
};
const results={};
for(const [name,source] of Object.entries(cases)) {
 const errors=[];
 const doc=parse(source,{scriptingEnabled:false,sourceCodeLocationInfo:true,onParseError:e=>errors.push(e.code)});
 const html=doc.childNodes.find(n=>n.tagName==='html');
 const body=html.childNodes.find(n=>n.tagName==='body');
 function text(node) {
  if(node.nodeName==='#text')return node.value;
  if(node.tagName && (node.namespaceURI!=='http://www.w3.org/1999/xhtml' || ['template','noscript','script','style'].includes(node.tagName)))return '';
  return (node.childNodes??[]).map(text).join('');
 }
 results[name]={bodyTextAfterContainerRemoval:text(body),errors};
}
process.stdout.write(JSON.stringify(results,null,2)+'\n');
