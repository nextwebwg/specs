import assert from 'node:assert/strict';
function payload(node) {
  return [node.nodeName,node.tagName,node.namespaceURI,node.attrs?.map(a=>[a.name,a.namespace??null,a.prefix??null,a.value]),node.value,node.data,
    (node.childNodes??[]).map(payload),node.content?payload(node.content):null];
}
// Independent audit of the public output, not the builder's accept/fallback
// decision: element origins/data and code/passive-context ownership must match.
export function auditPlacement(parser, root = parser.document, output = parser.output(root)) {
  const sourceNodes = new Set();
  const paths = new Map();
  const raw = node => parser.rawOwners.has(node)||['script','style'].includes(node.tagName);
  const protectedNode = node => node.content||(node.namespaceURI&&node.namespaceURI!=='http://www.w3.org/1999/xhtml')||raw(node);
  const read = (node,path=[]) => {
    sourceNodes.add(node);paths.set(node,path);
    const inside=protectedNode(node)?[...path,node]:path;
    for(const child of node.childNodes??[])read(child,inside);
    if(node.content)read(node.content,inside);
  };
  read(root);
  const used = new Set();
  const inspect = (node,path=[]) => {
    const origin=node.recognitionNode;
    if(node.tagName||node.nodeName==='#documentType'||node.nodeName==='#document-fragment'){
      assert.ok(sourceNodes.has(origin),`unrecognized ${node.tagName??node.nodeName}`);
      assert.ok(!used.has(origin),'duplicated source element/container');used.add(origin);
      assert.equal(node.tagName,origin.tagName);assert.equal(node.namespaceURI,origin.namespaceURI);
      assert.deepEqual(node.attrs,origin.attrs);
      assert.deepEqual(path,paths.get(origin),`changed protected context for ${node.tagName??node.nodeName}`);
      if(raw(origin))assert.deepEqual(payload(node),payload(origin),`changed code/text owner ${node.tagName}`);
    }
    const inside=sourceNodes.has(origin)&&protectedNode(origin)?[...path,origin]:path;
    for(const child of node.childNodes??[])inspect(child,inside);
    if(node.content)inspect(node.content,inside);
  };
  inspect(output);
  return output;
}
