import {LiveDOMParser} from './live-dom.mjs';
export async function runCases(origin) {
  const results = [];
  async function run(name, source, check, setup = () => {}) {
    const iframe = document.createElement('iframe');
    iframe.srcdoc = '<!doctype html><body>';
    const loaded = new Promise(resolve => iframe.onload = resolve);
    document.body.append(iframe); await loaded;
    const window = iframe.contentWindow;
    window.trace = [];
    try {
      setup(window);
      const parser = new LiveDOMParser(window.document);
      await parser.write('<!doctype html><body>' + source, true);
      await check(window, (condition, message) => { if (!condition) throw new Error(message); });
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
  return results;
}
