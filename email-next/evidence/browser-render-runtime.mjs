// Serialized trusted client runtime. No sender HTML/string is parsed as markup.
export function renderRuntime(token) {
 const channel=new MessageChannel(),port=channel.port1;
  port.onmessage=({data})=>{
   if(data?.kind!=='render'||data.token!==token)return;
   try {
    const {tree,images,policy,renderId,limits}=data;let count=0,textCount=0;
    if(!limits||['maxNodes','maxDepth','maxText','maxWidth','maxHeight','maxPixels'].some(k=>!Number.isSafeInteger(limits[k])||limits[k]<1))throw Error('local-limits');
    const common=new Set(['title','lang','dir','style']);
    const specific={img:['alt','width','height'],ol:['start','reversed'],li:['value'],td:['colspan','rowspan'],th:['colspan','rowspan','scope'],col:['span'],colgroup:['span']};
    const style=(element,value)=>{
     for(const declaration of value.split(';')) {
      if(!declaration)continue;
      const [name,v,...extra]=declaration.split(':');
      if(extra.length||(!policy.keywords[name]?.split(' ').includes(v)&&!(policy.colors.includes(name)&&(/^#[0-9a-f]{3}([0-9a-f]{3})?$/.test(v)||(name==='background-color'&&v==='transparent')))))throw Error('style-contract');
      element.style.setProperty(name,v);
     }
    };
    const build=(node,depth=0)=>{
     if(++count>limits.maxNodes||depth>limits.maxDepth)throw Error('tree-budget');
     if(typeof node==='string'){textCount+=node.length;if(textCount>limits.maxText)throw Error('text-budget');return document.createTextNode(node);}
     if(!node||!policy.elements.includes(node.element)||!Array.isArray(node.children)||typeof node.nodeId!=='string'||Object.keys(node).some(k=>!['element','attributes','children','nodeId','linkId'].includes(k)))throw Error('tree-contract');
     let element=document.createElement(node.element==='img'?'canvas':node.element);
     const attrs=node.attributes??{};
     for(const [key,value]of Object.entries(attrs)){
      if(typeof value!=='string'||(!common.has(key)&&!specific[node.element]?.includes(key)))throw Error('attribute-contract');
      if(key==='style')style(element,value);
      else if(node.element!=='img'||!['alt','width','height'].includes(key))element.setAttribute(key,value);
     }
     if(node.element==='img'){
      const image=images[node.nodeId];const alt=attrs.alt??'';
      if(image?.state==='pixels'){
       const bytes=new Uint8ClampedArray(image.rgba);
       if(!Number.isInteger(image.width)||!Number.isInteger(image.height)||image.width<1||image.height<1||image.width>limits.maxWidth||image.height>limits.maxHeight||image.width*image.height>limits.maxPixels||bytes.length!==image.width*image.height*4)throw Error('pixel-contract');
       element.width=image.width;element.height=image.height;
       element.getContext('2d').putImageData(new ImageData(bytes,image.width,image.height),0,0);
       element.className='client-image';
       if(alt){element.setAttribute('role','img');element.setAttribute('aria-label',alt);}else element.setAttribute('aria-hidden','true');
       if(attrs.width)element.style.width=attrs.width+'px';
       else if(attrs.height)element.style.width=(Number(attrs.height)*image.width/image.height)+'px';
      }else{const fallback=document.createElement('span');for(const attribute of element.attributes)fallback.setAttribute(attribute.name,attribute.value);fallback.textContent=alt;element=fallback;}
     }else{
      for(const child of node.children)element.append(build(child,depth+1));
     }
     if(node.linkId!==undefined){
      if(node.element!=='a'||typeof node.linkId!=='string')throw Error('link-contract');
      element.setAttribute('role','link');element.tabIndex=0;
      const activate=event=>{if(!event.isTrusted)return;event.preventDefault();port.postMessage({kind:'navigate',renderId,linkId:node.linkId});};
      element.addEventListener('click',activate);element.addEventListener('keydown',e=>{if(e.key==='Enter')activate(e);});
     }
     if(node.element==='table'){
      const wrapper=document.createElement('div');wrapper.className='client-table';wrapper.tabIndex=0;wrapper.setAttribute('role','region');wrapper.setAttribute('aria-label','Message table');wrapper.append(element);return wrapper;
     }
     return element;
    };
    const fragment=document.createDocumentFragment();for(const node of tree)fragment.append(build(node));
    document.body.replaceChildren(fragment);port.postMessage({kind:'rendered',renderId});
   }catch {document.body.replaceChildren(document.createTextNode('Message preview unavailable'));port.postMessage({kind:'rejected',renderId:data.renderId});}
  };
  port.start();parent.postMessage({kind:'email-next-render-ready',token},'*',[channel.port2]);
}
