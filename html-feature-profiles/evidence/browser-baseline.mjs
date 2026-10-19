import {chromium,firefox,webkit} from '../../self-closing-html/evidence/node_modules/playwright/index.mjs';
import {writeFileSync,readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const engines={chromium,firefox,webkit};
const paths={
 chromium:process.env.CHROMIUM_EXECUTABLE,
 firefox:process.env.FIREFOX_EXECUTABLE,
 webkit:process.env.WEBKIT_EXECUTABLE,
};
const reports=[];
for(const [engine,type] of Object.entries(engines)){
 const browser=await type.launch({headless:true,...paths[engine]?{executablePath:paths[engine]}:{}});
 try{
  const page=await browser.newPage();
  const cases=await page.evaluate(()=>{
   const source='<div id="empty"/><span id="after">tail</span>';
   globalThis.__profileProbeExecuted=0;
   return ['parseHTML','parseHTMLUnsafe'].map(method=>{
    if(typeof Document[method]!=='function')return {method,available:false};
    const parentOf=doc=>doc.querySelector('span')?.parentElement?.tagName??null;
    const baseline=Document[method](source);
    let reads=0;const options={get profile(){reads++;return 'self-closing'}};
    const explicit=Document[method](source,options);
    const withDoctype=Document[method]('<!DOCTYPE html PUBLIC "next">'+source);
    let unsupportedError=null;try{Document[method](source,{profile:'not-a-supported-profile'})}catch(e){unsupportedError=e.name}
    const untrusted='<script>globalThis.__profileProbeExecuted=1</script><img onerror="globalThis.__profileProbeExecuted=2"><a href="javascript:globalThis.__profileProbeExecuted=3">link</a>';
    const security=Document[method](untrusted);
    const custom=Document[method]('<user-avatar>light content</user-avatar>');
    let optionalSanitizer;try{const d=Document[method](untrusted,{profile:'self-closing',sanitizer:'default'});optionalSanitizer={scriptElements:d.querySelectorAll('script').length,eventAttributes:d.querySelectorAll('[onerror]').length,javascriptURLs:[...d.querySelectorAll('[href]')].filter(e=>e.getAttribute('href').startsWith('javascript:')).length}}catch(e){optionalSanitizer={error:e.name}}
    return {method,available:true,baselineMarkup:baseline.body.innerHTML,baselineParent:parentOf(baseline),explicitParent:parentOf(explicit),doctypeParent:parentOf(withDoctype),profileGetterReads:reads,unsupportedError,
     hasResolvedProfileRecord:!!explicit.htmlProfile,
     scriptElements:security.querySelectorAll('script').length,
     eventAttributes:security.querySelectorAll('[onerror]').length,
     javascriptURLs:[...security.querySelectorAll('[href]')].filter(e=>e.getAttribute('href').startsWith('javascript:')).length,
     customHostElements:custom.querySelectorAll('user-avatar').length,optionalDefaultSanitizer:optionalSanitizer,sourceScriptExecuted:globalThis.__profileProbeExecuted!==0};
   });
  });
  reports.push({engine,version:browser.version(),cases});
 }finally{await browser.close()}
}
const report={runtime:process.version,scope:'Unmodified browser API baseline, not native support for proposed profile options. Unknown dictionary options can be ignored.',sourceSHA256:createHash('sha256').update(readFileSync(new URL('./browser-baseline.mjs',import.meta.url))).digest('hex'),reports};
writeFileSync(new URL('./browser-baseline-results.json',import.meta.url),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(reports));
