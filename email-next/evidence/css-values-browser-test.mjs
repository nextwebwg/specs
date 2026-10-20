// Client baseline unit resolution. This does not certify layout or accessibility.
import {readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const {chromium}=await import(process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE);
const baseline=await readFile(new URL('./presentation-defaults.css',import.meta.url),'utf8');
const browser=await chromium.launch({headless:true,...(process.env.EMAIL_NEXT_CHROMIUM_EXECUTABLE?{executablePath:process.env.EMAIL_NEXT_CHROMIUM_EXECUTABLE}:{})});
try{
 const page=await browser.newPage();
 for(const root of [16,24]){
  await page.setContent('<!doctype html><style>'+baseline+'</style><p style="font-size:20px">Parent <small>Small</small><sub>Sub</sub></p><div style="width:100px"><canvas width="500" height="100" style="max-inline-size:100%;height:auto"></canvas></div>');
  await page.evaluate(root=>document.documentElement.style.fontSize=root+'px',root);
  const actual=await page.evaluate(()=>{
   const p=getComputedStyle(document.querySelector('p')),small=getComputedStyle(document.querySelector('small')),sub=getComputedStyle(document.querySelector('sub'));
   return {bodyFont:getComputedStyle(document.body).fontSize,margin:p.marginBottom,line:p.lineHeight,smallFont:small.fontSize,smallLine:small.lineHeight,subFont:sub.fontSize,subOffset:sub.bottom,imageWidth:document.querySelector('canvas').getBoundingClientRect().width};
  });
  assert.deepEqual(actual,{bodyFont:root+'px',margin:root+'px',line:'30px',smallFont:'17.5px',smallLine:'26.25px',subFont:'15px',subOffset:'-3.75px',imageWidth:100});
 }
 console.log(JSON.stringify({result:'pass',chromium:browser.version(),rootSizes:[16,24],scope:'Client baseline rem/em/percentage and unitless line-height composition only'}));
}finally{await browser.close();}
