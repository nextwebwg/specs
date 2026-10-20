// Local test adapter: argv[2] is a pinned parse5 module file URL.
const {parse}=await import(process.argv[2]);
let input='';for await(const chunk of process.stdin)input+=chunk;
const errors=[];
const root=parse(JSON.parse(input),{scriptingEnabled:false,onParseError:e=>errors.push(e.code)});
function convert(node) {
 if(node.nodeName==='#text')return node.value;
 if(!node.tagName)return {tag:'#other',children:[]};
 return {tag:`{${node.namespaceURI}}${node.tagName}`,
   attributes:Object.fromEntries(node.attrs.map(a=>[a.namespace?`{${a.namespace}}${a.name}`:a.name,a.value])),
   children:(node.tagName==='template' && node.content?node.content.childNodes:node.childNodes).map(convert)};
}
process.stdout.write(JSON.stringify({root:convert(root.childNodes.find(n=>n.tagName==='html')),errors}));
