import {LiveDOMParser} from './live-dom.mjs';
export async function runCases(origin) {
  const results = [];
  async function run(name, source, check, setup = () => {}, between = () => {}) {
    const iframe = document.createElement('iframe');
    iframe.srcdoc = '<!doctype html><body>';
    const loaded = new Promise(resolve => iframe.onload = resolve);
    document.body.append(iframe); await loaded;
    const window = iframe.contentWindow;
    window.trace = [];
    try {
      setup(window);
      const parser = new LiveDOMParser(window.document);
      const chunks=Array.isArray(source)?source:[source];
      for(let i=0;i<chunks.length;i++){
        await parser.write((i===0?'<!doctype html><body>':'')+chunks[i],i===chunks.length-1);
        if(i<chunks.length-1)await between(window,parser,i);
      }
      await check(window, (condition, message) => { if (!condition) throw new Error(message); }, parser);
      results.push({name, pass:true});
    } catch (error) { results.push({name, pass:false, error:String(error)}); }
    finally { iframe.remove(); }
  }
  const attacks = [
    '<textarea/><img src="'+origin+'/probe?textarea" onerror="trace.push(\'BAD\')"></textarea>',
    '<select/><img src="'+origin+'/probe?select" onerror="trace.push(\'BAD\')"></select>',
    '<style/><img src="'+origin+'/probe?direct" onerror="trace.push(\'BAD\')"></style>',
    '<div/><svg></div><style><img src="'+origin+'/probe?namespace" onerror="trace.push(\'BAD\')"></style></svg>',
    '<div><x-box/></div><svg></x-box><title><style></title><img src="'+origin+'/probe?expired" onerror="trace.push(\'BAD\')"></style>',
  ];
  for (const [i, source] of attacks.entries()) await run('recognized text remains text '+i, source, (w,c) => {
    c(w.document.querySelectorAll('img').length===0,'no new image');
    c(w.trace.length===0,'no attack executed');
  });
  await run('template execution and resource boundary',
    '<template/><small/><script>trace.push("BAD")</script><img src="'+origin+'/probe?template" onerror="trace.push(\'BAD\')">',
    async(w,c)=>{
      await new Promise(resolve=>setTimeout(resolve,100));
      c(w.trace.length===0,'template script/handler remains inactive');
      c(w.document.querySelectorAll('script,img').length===0,'nothing escapes template');
      c(w.document.querySelector('template').content.querySelector('img').ownerDocument.defaultView===null,'image belongs to inactive template document');
    });
  await run('handler positive control', '<img src="'+origin+'/probe?positive" onerror="trace.push(\'positive\')">', async(w,c)=>{
    const until=Date.now()+2000;
    while(!w.trace.length&&Date.now()<until)await new Promise(resolve=>setTimeout(resolve,10));
    c(w.trace[0]==='positive','ordinary image handlers actually run');
  });
  await run('formatting closure and script checkpoint',
    '<small id="empty"/><script>trace.push([document.getElementById("empty").childNodes.length,document.currentScript.parentNode.tagName,!!document.querySelector("span")])</script><span>tail</span>',
    (w,c)=>c(JSON.stringify(w.trace)==='[[0,"BODY",false]]','script sees empty small, itself under body, and no later span'));
  await run('script mutation ownership',
    '<small id="empty"/><script>document.getElementById("empty").append("owned")</script><span>tail</span>',
    (w,c)=>{c(w.document.getElementById('empty').textContent==='owned','script-owned child retained');c(w.document.querySelector('span').parentNode.tagName==='BODY','source span follows small');});
  await run('custom element callback placement', '<x-rec/><span>tail</span>', (w,c)=>{
    c(w.trace[0]==='BODY','connected callback sees projected parent');
    c(w.document.querySelector('x-rec').childNodes.length===0,'custom element empty');
  }, w=>w.customElements.define('x-rec',class extends w.HTMLElement{connectedCallback(){w.trace.push(this.parentNode.tagName);}}));
  await run('native table row/cell placement',
    '<table id="t"><tbody><tr><td/><td>two</td></tr><tr/></tbody></table><p id="tail">tail</p>',(w,c)=>{
      const table=w.document.getElementById('t');
      c(table.rows.length===2,'two native table rows');
      c(table.rows[0].cells.length===2&&table.rows[0].cells[0].textContent===''&&table.rows[0].cells[1].textContent==='two','empty first cell and populated second cell');
      c(table.rows[1].cells.length===0,'self-closed final row empty');
      c(table.getBoundingClientRect().width>0,'native table layout occurs');
      c(table.nextElementSibling.id==='tail','following paragraph stays after table');
    });
  await run('nested identical wrappers close predictably','<nav><nav/></nav><p id="tail">tail</p>',(w,c)=>{
    c(w.document.getElementById('tail').parentNode.tagName==='BODY','paragraph outside both nav elements');
    c(w.document.querySelectorAll('nav').length===2,'exactly two authored nav elements');
  });
  await run('formatting reconstruction creates no ghost element','<h2><small/></h2><h1>tail</h1>',(w,c)=>{
    c(w.document.querySelectorAll('small').length===1,'one small for one source token');
    c(w.document.querySelector('h1').textContent==='tail'&&w.document.querySelector('h1').children.length===0,'no reconstructed small in following heading');
  });
  await run('pre newline belongs after the empty element','<pre/>\n<span>tail</span>',(w,c)=>{
    const pre=w.document.querySelector('pre');
    c(pre.childNodes.length===0&&pre.nextSibling.nodeType===3&&pre.nextSibling.data==='\n','newline preserved outside pre');
  });
  await run('a live script data-block switch stays inactive',
    ['<small/><script>','trace.push("BAD")</script><p>tail</p>'],(w,c)=>{
      c(w.trace.length===0,'no code executed after app made script a data block');
    },()=>{},w=>{w.document.querySelector('script').type='application/json';});
  await run('owned text survives protected-context recovery',
    ['<p id="p">original</p>','<div/><svg></div><style><img src="'+origin+'/probe?owned-recovery" onerror="trace.push(\'BAD\')"></style></svg>'],(w,c)=>{
      c(w.document.getElementById('p').firstChild===w.ownedText&&w.ownedText.data==='owned','text identity and app data retained');
      c(w.document.querySelectorAll('img').length===0,'recovery creates no image');
    },()=>{},w=>{w.ownedText=w.document.getElementById('p').firstChild;w.ownedText.data='owned';});
  return results;
}
