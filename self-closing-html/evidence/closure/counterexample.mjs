import fs from 'node:fs';
import sanitizeHtml from 'sanitize-html';
import {parse,serialize} from 'parse5';
import {parseClosure} from './parser.mjs';
import {createSafeParser} from './safe-parse.mjs';
const input='<svg><mtext><style/><table/><style/><img data-probe src=x onerror="probe()">';
const policy={allowedTags:[...sanitizeHtml.defaults.allowedTags,'style','template','select','option','x-box','svg','math','mtext','mglyph','foreignObject','img'],allowedAttributes:{'*':['class','id','data-probe'],img:['src']},allowVulnerableTags:true};
const legacySanitized=sanitizeHtml(input,policy);
const unsafe=parseClosure(legacySanitized);
const safe=createSafeParser();
try{
 const result=safe.parse(legacySanitized,{profile:'self-closing'});
 const report={scope:'Custom permissive sanitize-html 2.18.1 policy explicitly allows vulnerable style tags but does not allow event-handler attributes. Not a default-policy vulnerability claim. Safe output is a DOM result, not reparsed source.',input,legacySanitized,legacyDOM:serialize(parse(legacySanitized)),unsafeDOM:unsafe.html,safeDOMForInspection:result.root.outerHTML,safeHandlers:result.document.querySelectorAll('[onerror],script').length};
 fs.writeFileSync(new URL('./counterexample-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
 if(report.safeHandlers)process.exitCode=1;
}finally{safe.close();}
