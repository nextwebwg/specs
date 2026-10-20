// Exact envelope3 presentation. These are authenticated author statements only
// after the caller completes MLS, identity, context and operation acceptance.
export function validatePresentation(value,author,audience,isPrincipal) {
 if(!value||typeof value!=='object'||Array.isArray(value)||Object.keys(value).length!==4||!['subject','authoredAt','to','cc'].every(k=>Object.hasOwn(value,k)))return false;
 if(typeof value.subject!=='string'||/[\u0000-\u001f\u007f-\u009f]/u.test(value.subject)||/[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/u.test(value.subject))return false;
 if(typeof value.authoredAt!=='string'||(value.authoredAt!==''&&(!/^(0|[1-9][0-9]{0,19})$/.test(value.authoredAt)||BigInt(value.authoredAt)>18446744073709551615n)))return false;
 for(const key of ['to','cc'])if(!Array.isArray(value[key])||value[key].some(p=>typeof p!=='string'||!isPrincipal(p))||new Set(value[key]).size!==value[key].length)return false;
 if(value.to.some(p=>value.cc.includes(p)))return false;
 const named=new Set([author,...value.to,...value.cc]);return named.size===audience.length&&audience.every(p=>named.has(p));
}
