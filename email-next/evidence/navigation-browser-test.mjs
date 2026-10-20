// Focused parser agreement in a real browser; no destination is fetched.
import assert from 'node:assert/strict';
import {validateNavigationUrl} from './navigation-url.mjs';
const {chromium}=await import(process.env.EMAIL_NEXT_PLAYWRIGHT_MODULE);
const inputs=[
 'HTTPS://Example.test:443/a/../b?q=x#f','http://example.test/',
 '/path','//example.test','javascript:alert(1)','data:text/html,x',
 'mailto:a@example.test','https:example.test','https:///example.test',
 'https://a:b@example.test','https://@example.test','https://:x@example.test',
 ' https://example.test','https://exam\nple.test','https://example.test/\u007f',
 'https://example.test\\@evil.test','https://[broken','https://example.test:99999',
 'https://example.test/\ud800','https://bücher.example/a%20b',
 'https://exam%70le.test/','https://0x7f.1/',
 'https://example.test/a/%2e%2E/b?x=/../#../','https://xn--8i7caa/',
 'https://example.test/%s','https://[2001:0DB8:0:0:1:0:0:1]:443/',
 'https://[::ffff:192.0.2.1]/','https://[1::2::3]/',
 'https://[::ffff:192.00.2.1]/','https://[::ffff:192.0.2.256]/',
 "https://example.test/é?x=é+'&y=%252F#é"
];
const browser=await chromium.launch({headless:true,...(process.env.EMAIL_NEXT_CHROMIUM_EXECUTABLE?{executablePath:process.env.EMAIL_NEXT_CHROMIUM_EXECUTABLE}:{})});
try{
 const page=await browser.newPage();
 const actual=await page.evaluate(({source,inputs})=>{
  const check=(0,eval)('('+source+')');return inputs.map(check);
 },{source:validateNavigationUrl.toString(),inputs});
 inputs.forEach((input,index)=>assert.deepEqual(actual[index],validateNavigationUrl(input),input));
 console.log(JSON.stringify({cases:inputs.length,node:process.version,chromium:browser.version(),result:'pass',scope:'Focused HTTP(S) navigation parser agreement; no destination fetch or full conformance claim.'}));
}finally{await browser.close();}
