// Reference selector/precedence model only. This does not implement HTML parsing,
// browser sanitization, a full HTTP stack, or the proposed native API options.
const syntax = message => new DOMException(message, 'SyntaxError');
const unsupported = message => new DOMException(message, 'NotSupportedError');
const identifier = /^[a-z][a-z0-9-]*$/;
const freeze = record => Object.freeze({...record,
 features:Object.freeze([...record.features]),
 featureRevisions:Object.freeze({...record.featureRevisions}),
});
const ordinary = (requested=null,source='legacy') => freeze({requested,features:[],featureRevisions:{},preset:null,revision:null,source,status:'legacy'});

export function parseSelector(value,{header=false}={}) {
 if(typeof value==='symbol')throw new TypeError('A symbol cannot convert to DOMString');
 const text=String(value);
 // HTTP stack handling is outside this model. Recognize only the allowed bare
 // token-list subset of Structured Fields; other item types/parameters fail.
 if(header && /[^\x20-\x7e\t]/.test(text))throw syntax('Invalid header bytes');
 const trim=header ? /^[ \t]+|[ \t]+$/g : /^[\t\n\f\r ]+|[\t\n\f\r ]+$/g;
 const entries=text.split(',').map(entry=>entry.replace(trim,''));
 if(entries.some(entry=>!identifier.test(entry)))throw syntax('Invalid selector');
 if(new Set(entries).size!==entries.length)throw syntax('Duplicate selector');
 if(entries.length>1 && entries.some(entry=>entry==='next'||entry==='inherit'))throw syntax('Reserved selector must stand alone');
 return entries;
}

function validate(features,revisions,context) {
 for(const feature of features){
  const available=context.supported[feature];
  if(!available || !available.includes(revisions[feature]))throw unsupported('Unsupported feature revision');
 }
 if(context.compatible && !context.compatible(features))throw unsupported('Unsupported combination');
}

function resolve(entries,requested,source,context) {
 if(entries[0]==='inherit')throw unsupported('inherit is API-only');
 const preset=entries[0]==='next';
 const manifest=context.manifest;
 const features=new Set(preset?manifest.next:entries);
 const pending=[...features];
 for(let i=0;i<pending.length;i++){
  const spec=manifest.registry[pending[i]];
  if(!spec)throw unsupported('Unknown feature');
  for(const dependency of spec.requires??[]){if(!features.has(dependency)){features.add(dependency);pending.push(dependency);}}
 }
 const canonical=[...features].sort();
 const revisions=Object.fromEntries(canonical.map(feature=>[feature,manifest.registry[feature].revision]));
 validate(canonical,revisions,context);
 return freeze({requested,features:canonical,featureRevisions:revisions,preset:preset?'next':null,revision:manifest.revision,source,status:'active'});
}

export function resolveAPIProfile(value,context) {
 // The absent/undefined path must not inspect an ambient caller or preset.
 if(value===undefined)return ordinary();
 if(typeof value==='symbol')throw new TypeError('A symbol cannot convert to DOMString');
 const text=String(value);
 const entries=parseSelector(text);
 if(entries[0]==='inherit'){
  const caller=context.caller;
  validate(caller.features,caller.featureRevisions,context);
  return freeze({...caller,requested:'inherit',source:'api'});
 }
 return resolve(entries,text,'api',context);
}

export function resolveNavigationProfile({header=null,doctype=null},context) {
 if(header!==null && header!==undefined)return resolve(parseSelector(header,{header:true}),String(header),'header',context);
 if(doctype!==null && doctype!==undefined)return resolve(parseSelector(doctype),String(doctype),'doctype',context);
 return ordinary();
}
