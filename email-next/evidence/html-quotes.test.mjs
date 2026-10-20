import test from 'node:test';import assert from 'node:assert/strict';
import {scanHtmlQuotes,reconstructHtmlQuotes} from './html-quotes.mjs';
test('exact interleaving and entity equivalence retain original source spans',()=>{
 const source='<p>Le 20 octobre, Alice a écrit :</p>\r\n<blockquote><p>A &amp; B?</p></blockquote><p>Oui.</p>';
 const result=reconstructHtmlQuotes(source,[{id:'parent',html:'<p>A &#38; B?</p>'}]);assert.equal(result.nodes[2].presentation,'repeated-quote');assert.equal(source.slice(result.nodes[2].start,result.nodes[2].end),'<blockquote><p>A &amp; B?</p></blockquote>');assert.equal(result.nodes[0].text,'Le 20 octobre, Alice a écrit :');assert.equal(result.nodes.at(-1).text,'Oui.');assert.equal(result.nodes.map(n=>source.slice(n.start,n.end)).join(''),source);
});
test('UTF16 astral offsets precede CRLF and entity decoding',()=>{const source='<p>😀\r\n&amp;</p><blockquote><p>😀\n&amp;</p></blockquote>';const parsed=scanHtmlQuotes(source);assert.equal(parsed.nodes[0].end,16);assert.equal(parsed.nodes[0].text,'😀\n&');assert.equal(source.slice(parsed.nodes[0].parts[0].start,parsed.nodes[0].parts[0].end),'😀\r\n&amp;');assert.equal(reconstructHtmlQuotes(source,[{id:'p',html:'<p>😀\n&#38;</p>'}]).nodes[1].presentation,'repeated-quote');});
test('changed text and duplicate parent occurrences stay visible',()=>{for(const html of ['<p>Thursday</p>','<p>Tuesday</p><p>Tuesday</p>'])assert.equal(reconstructHtmlQuotes('<blockquote><p>Tuesday</p></blockquote>',[{id:'p',html}]).nodes[0].presentation,'visible');});
test('nested repaired or unsupported markup falls back to whole untouched source',()=>{for(const source of ['<blockquote><blockquote><p>x</p></blockquote></blockquote>','<p>missing','<p>x<p>y</p>','<p class="x">x</p>','<script>bad()</script>','<!--x--><p>x</p>','<p><b>x</b></p>']){const result=scanHtmlQuotes(source);assert.equal(result.state,'visible-source');assert.deepEqual(result.nodes,[{kind:'source',start:0,end:source.length,text:source}]);}});
test('invalid replacement/control references and unknown entities never guess',()=>{for(const value of ['&#0;','&#xD800;','&#128;','&#x110000;','&#xFFFF;','&nbsp;','&amp','&#1;'])assert.equal(scanHtmlQuotes('<p>'+value+'</p>').state,'visible-source');assert.equal(scanHtmlQuotes('<p>&lt;&gt;&quot;&apos;&#x1F600;<br>ok</p>').nodes[0].text,'<>"\'😀\nok');});
test('parent quote contents cannot become unquoted sources or bridge a quote',()=>{const result=reconstructHtmlQuotes('<blockquote><p>a</p><p>b</p></blockquote>',[{id:'p',html:'<p>a</p><blockquote><p>x</p></blockquote><p>b</p>'}]);assert.equal(result.nodes[0].presentation,'visible');});
test('localized attribution is visible regardless of matched or unmatched quotation',()=>{
 for(const label of ['Am 20. Oktober schrieb Alice:','2026年10月20日、Alice さんは書きました:','في 20 أكتوبر، كتب Alice:']){
  const source=`<p>${label}</p><blockquote><p>Day?</p></blockquote><p>Tuesday.</p><blockquote><p>Place?</p></blockquote><p>Library.</p>`;
  const result=reconstructHtmlQuotes(source,[{id:'p',html:'<p>Day?</p><p>Place?</p>'}]);
  assert.deepEqual(result.nodes.map(n=>n.presentation),['visible','repeated-quote','visible','repeated-quote','visible']);
  assert.equal(result.nodes[0].text,label);assert.equal(result.nodes.map(n=>source.slice(n.start,n.end)).join(''),source);
  assert.ok(reconstructHtmlQuotes(source,[]).nodes.every(n=>n.presentation==='visible'));
 }
});
test('labels cannot authorize hiding unmarked copies or unfamiliar quote markup',()=>{
 for(const source of ['<p>Am Montag schrieb Alice:</p><p>Day?</p>','<p>差出人: Alice</p><blockquote style="color:red"><p>Day?</p></blockquote>','<div class="quote"><p>Day?</p></div>']){
  const result=reconstructHtmlQuotes(source,[{id:'p',html:'<p>Day?</p>'}]);assert.ok(result.nodes.every(n=>n.presentation!=='repeated-quote'));assert.equal(result.source,source);
 }
});
test('inert div wrappers and attributed blockquotes preserve exact source and interleaving',()=>{
 const source='<div class="reply"><div>Am Montag schrieb Alice:</div><blockquote type="cite" cite="https://untrusted.invalid/" class="quoted"><div><p>Day?</p></div></blockquote><div>Tuesday.</div><blockquote><div>Place?</div></blockquote><div>Library.</div></div>';
 const result=reconstructHtmlQuotes(source,[{id:'p',html:'<div class="body"><div>Day?</div><div>Place?</div></div>'}]);
 assert.equal(result.state,'mapped');assert.equal(result.nodes.filter(n=>n.presentation==='repeated-quote').length,2);
 assert.equal(result.nodes.map(n=>source.slice(n.start,n.end)).join(''),source);
 assert.deepEqual(result.nodes.filter(n=>n.kind==='paragraph').map(n=>n.text),['Am Montag schrieb Alice:','Tuesday.','Library.']);
 for(const quote of result.nodes.filter(n=>n.kind==='quote'))assert.equal(quote.children.map(n=>source.slice(n.start,n.end)).join(''),source.slice(quote.children[0].start,quote.children.at(-1).end));
 for(const parents of [[],[{id:'p',html:'<div>Changed?</div>'}],[{id:'p',html:'<p>Day?</p>'},{id:'q',html:'<div>Day?</div>'}]])assert.ok(reconstructHtmlQuotes(source,parents).nodes.every(n=>n.presentation!=='repeated-quote'));
});
test('attributes never supply author authority and malformed wrappers preserve whole source',()=>{
 for(const source of ['<blockquote class="a" class="b"><p>x</p></blockquote>','<blockquote onclick="x"><p>x</p></blockquote>','<blockquote type=cite><p>x</p></blockquote>','<div><p>x</p>','<div><blockquote><div><blockquote><p>x</p></blockquote></div></blockquote></div>'])assert.equal(scanHtmlQuotes(source).state,'visible-source');
 const source='<div class="quoted"><div>x</div></div>';assert.ok(reconstructHtmlQuotes(source,[{id:'p',html:'<p>x</p>'}]).nodes.every(n=>n.presentation!=='repeated-quote'));
});
