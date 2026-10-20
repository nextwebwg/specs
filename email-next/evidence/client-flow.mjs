import {reconstructQuotes} from './legacy-quotes.mjs';
import {mountMessage} from './browser-render-host.mjs';
let richController,renderGeneration=0;
let state,selectedId="project",category="contacts",loadingGeneration=0;
const replyChoices=new Map(),subjects=new Map(),focusedBranches=new Map(),senderChoices=new Map();
const drafts=new Map(),selectedByCategory={contacts:"project"};
const root=document.querySelector('#conversation'),status=document.querySelector('#status');
function securityIcon(protectedMessage){const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('aria-hidden','true');const body=document.createElementNS(svg.namespaceURI,'rect');for(const [key,value]of Object.entries({x:5,y:10,width:14,height:11,rx:2}))body.setAttribute(key,String(value));const shackle=document.createElementNS(svg.namespaceURI,'path');shackle.setAttribute('d',protectedMessage?'M8 10V7a4 4 0 0 1 8 0v3':'M9 10V7a4 4 0 0 1 8 0');svg.append(body,shackle);return svg;}
function card(name,meta,text){const article=document.createElement('article');article.dataset.initial=name[0];const heading=document.createElement('h2');heading.textContent=name;const details=document.createElement('details');details.className='message-details';const summary=document.createElement('summary');summary.textContent='';const isFile=name==='Attachment',protectedMessage=meta.startsWith('Protected')||meta.startsWith('Authenticated');summary.setAttribute('aria-label',isFile?'File details':protectedMessage?'Protected message details':'Unencrypted message details');summary.title=isFile?'File details':protectedMessage?'Protected':'Unencrypted';if(isFile)summary.textContent='⋯';else summary.append(securityIcon(protectedMessage));const detail=document.createElement('p');detail.className='meta';detail.textContent=meta;details.append(summary,detail);const body=document.createElement('div');body.className='message-body';body.textContent=text;article.append(heading,details,body);root.append(article);return article;}
function render(value){
 renderGeneration++;richController?.dispose();richController=null;state=value;selectedId=value.selectedThread?.id??'project';root.replaceChildren();
 const selected=value.selectedThread??{title:'Alice, Bob',participants:[{name:'Alice'},{name:'Bob'}]};
 selectedByCategory[selected.contact===false?'other':'contacts']=selectedId;document.querySelector('#thread-title').textContent=selected.title;
 document.querySelector('#thread-subtitle').textContent=(selected.participants??[]).map(p=>p.name??p.address).join(', ');
 document.querySelector('#participant-avatar').textContent=initials(selected.title);renderThreads();
 if(state.question){
  const question=card('Alice','Protected question · an ordinary-email copy was also authorized',state.question.text);bindReply(question,value.questionReplyTarget);
  for(const option of state.question.options){const button=document.createElement('button');button.textContent=option.label;const action=crypto.randomUUID().replaceAll('-','');button.addEventListener('click',async()=>{button.disabled=true;try{await post('/answer',{action,option:option.id,token:value.token});}finally{button.disabled=false;}});question.append(button);}reactionControls(question,value.questionReplyTarget);
 }
 attachmentCards();richCards();
 for(const event of state.timeline??[]){const answer=event.kind==='answer',name=event.sender??(answer?'Bob':'Carol');const article=card(name,answer?'Authenticated structured answer · configured device identity':'Ordinary email · not an authenticated structured answer',event.text);bindReply(article,event.replyTarget);if(answer){const context=document.createElement('p');context.className='reply-context';context.textContent=state.question.text;article.insertBefore(context,article.querySelector('.message-body'));}else ordinaryBody(article,event);reactionControls(article,event.reactionTarget??event.replyTarget);}
 applyThreadFocus();renderSenderAccount();updateReplyContext();requestAnimationFrame(()=>{root.scrollTop=root.scrollHeight;drawReplyConnector();});
}
function initials(title){return title.split(/[, ]+/).filter(Boolean).slice(0,2).map(x=>x[0]).join('').toUpperCase();}
function renderThreads(){
 const list=document.querySelector('#thread-list');list.replaceChildren();
 for(const name of ['contacts','other']){const tab=document.querySelector('#'+name+'-tab');tab.setAttribute('aria-selected',String(category===name));tab.tabIndex=category===name?0:-1;}
 list.setAttribute('aria-label',category==='contacts'?'Contact conversations':'Other conversations');
 const threads=(state.threads??[{id:'project',title:'Alice, Bob',contact:true,preview:state.question?.text??'',activity:0}]).filter(t=>category==='contacts'?t.contact:!t.contact).sort((a,b)=>b.activity-a.activity);
 for(const thread of threads){const button=document.createElement('button');button.className='thread-item';button.dataset.thread=thread.id;button.setAttribute('aria-current',String(thread.id===selectedId));const avatar=document.createElement('span');avatar.className='thread-avatar';avatar.textContent=initials(thread.title);avatar.setAttribute('aria-hidden','true');const copy=document.createElement('span');copy.className='thread-copy';const title=document.createElement('strong');title.textContent=thread.title;const preview=document.createElement('span');preview.textContent=thread.preview;copy.append(title,preview);button.append(avatar,copy);button.addEventListener('click',()=>selectThread(thread.id));list.append(button);}
 if(!threads.length){const empty=document.createElement('p');empty.className='empty-list';empty.textContent='No conversations here yet.';list.append(empty);}
}
async function selectThread(id){
 drafts.set(selectedId,document.querySelector('#reply').value);const generation=++loadingGeneration;status.textContent='';
 try{const response=await fetch('/state?thread='+encodeURIComponent(id));if(!response.ok)throw Error('Conversation unavailable');const value=await response.json();if(generation!==loadingGeneration)return;selectedByCategory[category]=id;render(value);document.querySelector('#reply').value=drafts.get(id)??'';}catch(error){if(generation===loadingGeneration)status.textContent=error.message;}
}
for(const name of ['contacts','other'])document.querySelector('#'+name+'-tab').addEventListener('click',()=>{
 category=name;const eligible=(state.threads??[]).filter(t=>name==='contacts'?t.contact:!t.contact).sort((a,b)=>b.activity-a.activity);const remembered=eligible.find(t=>t.id===selectedByCategory[name]);renderThreads();if(remembered||eligible[0])selectThread((remembered??eligible[0]).id);
});
document.querySelector('.inbox-tabs').addEventListener('keydown',event=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(event.key)){event.preventDefault();const next=event.key==='Home'?'contacts':event.key==='End'?'other':category==='contacts'?'other':'contacts';const tab=document.querySelector('#'+next+'-tab');tab.click();tab.focus();}});
async function post(path,value){
 const target=selectedId,nonce=state.nonce;status.textContent='Sending…';
 try{const response=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json','X-Client-Session':nonce,'X-Conversation-ID':target},body:JSON.stringify(value)});if(!response.ok)throw new Error(await response.text());const result=await response.json();if(selectedId===target){render(result);status.textContent='Delivered.';}else{state={...state,threads:result.threads};renderThreads();}return result;}catch(error){status.textContent=error.message;return false;}
}
document.querySelector('#send-reply').addEventListener('click',async()=>{
 const input=document.querySelector('#reply'),button=document.querySelector('#send-reply'),text=input.value,target=selectedId,replyTo=chosenReply(),subject=document.querySelector('#thread-subject').value;
 if(!text.trim()||(replyTo===null&&!subject.trim()))return;const account=selectedAccount();if(!account?.enabled){status.textContent='Choose an available sending account.';return;}button.disabled=true;
 try{const result=await post('/reply',{text,account:account.id,...(state.replyTargets?{replyTo}:{}),...(replyTo===null?{subject}:{})});if(result){if(result.selectedThread?.id!==target)senderChoices.set(result.selectedThread.id,account.id);renderSenderAccount();drafts.delete(target);replyChoices.delete(target);if(selectedId===result.selectedThread?.id){if(input.value===text)input.value='';subjects.delete(target);subjects.delete(selectedId);updateReplyContext();root.scrollTop=root.scrollHeight;input.focus();}}}finally{button.disabled=false;}
});
function selectedAccount(){const id=senderChoices.has(selectedId)?senderChoices.get(selectedId):(state.senderAccounts?.find(a=>a.enabled)?.id??'personal');return state.senderAccounts?.find(a=>a.id===id)??(!state.senderAccounts?{id:'personal',address:'carol@example.invalid',enabled:true}:null);}
function renderSenderAccount(){
 const button=document.querySelector('#sender-account'),menu=document.querySelector('#sender-options'),account=selectedAccount();button.replaceChildren(document.createTextNode(account?.address??'Choose sender'));const chevron=document.createElement('span');chevron.textContent='⌄';chevron.setAttribute('aria-hidden','true');button.append(chevron);button.title=account?.address??'Choose an available account';button.setAttribute('aria-expanded','false');menu.hidden=true;menu.replaceChildren();
 for(const option of state.senderAccounts??[]){const item=document.createElement('button');item.type='button';item.setAttribute('role','menuitemradio');item.setAttribute('aria-checked',String(option.id===account?.id));item.disabled=!option.enabled;const address=document.createElement('span');address.textContent=option.address;const label=document.createElement('small');label.textContent=option.label;item.append(address,label);item.addEventListener('click',()=>{senderChoices.set(selectedId,option.id);renderSenderAccount();button.focus();});menu.append(item);}
}
document.querySelector('#sender-account').addEventListener('click',()=>{const menu=document.querySelector('#sender-options'),button=document.querySelector('#sender-account'),opening=menu.hidden;menu.hidden=!opening;button.setAttribute('aria-expanded',String(opening));if(opening)menu.querySelector('button:not(:disabled)')?.focus();});
document.querySelector('.sender-control').addEventListener('focusout',event=>{if(!event.currentTarget.contains(event.relatedTarget)){document.querySelector('#sender-options').hidden=true;document.querySelector('#sender-account').setAttribute('aria-expanded','false');}});
document.querySelector('#sender-options').addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();document.querySelector('#sender-options').hidden=true;document.querySelector('#sender-account').setAttribute('aria-expanded','false');document.querySelector('#sender-account').focus();}else if(['ArrowUp','ArrowDown','Home','End'].includes(event.key)){event.preventDefault();const items=[...event.currentTarget.querySelectorAll('button:not(:disabled)')],index=items.indexOf(document.activeElement),next=event.key==='Home'?0:event.key==='End'?items.length-1:(index+(event.key==='ArrowDown'?1:-1)+items.length)%items.length;items[next]?.focus();}});
document.querySelector('#reply').addEventListener('input',()=>{if(!replyChoices.has(selectedId)&&state.replyTargets)replyChoices.set(selectedId,visibleTargets().at(-1)?.id);});
document.querySelector('#thread-subject').addEventListener('input',event=>subjects.set(selectedId,event.target.value));
document.querySelector('#new-thread').addEventListener('click',()=>{replyChoices.set(selectedId,null);focusedBranches.delete(selectedId);render(state);updateReplyContext();document.querySelector('#thread-subject').focus();});
document.querySelector('#reply-context').addEventListener('click',()=>{const id=chosenReply();if(id===null){replyChoices.delete(selectedId);updateReplyContext();return;}const message=document.getElementById('reply-'+id);message?.scrollIntoView({block:'center',behavior:'smooth'});message?.focus({preventScroll:true});});
function chosenReply(){return replyChoices.has(selectedId)?replyChoices.get(selectedId):visibleTargets().at(-1)?.id;}
function bindReply(article,id){
 if(!id)return;article.id='reply-'+id;article.tabIndex=-1;
 const reply=document.createElement('button');reply.className='select-reply';reply.textContent='↩';reply.title='Reply to this message';reply.setAttribute('aria-label','Reply to this message');reply.addEventListener('click',()=>{focusedBranches.set(selectedId,id);replyChoices.set(selectedId,id);render(state);document.querySelector('#reply').focus();});
 const open=document.createElement('button');open.className='open-thread';open.textContent='Open thread';open.addEventListener('click',()=>openThread(id));article.append(reply);article.insertBefore(open,article.querySelector('.message-body'));
 article.querySelector('.message-body').addEventListener('click',event=>{if(!event.target.closest('button,a,details')&&!window.getSelection()?.toString())openThread(id);});
}
function branchIds(){const anchor=focusedBranches.get(selectedId);if(!anchor)return null;const included=new Set([anchor]);for(const target of state.replyTargets??[])if(included.has(target.parent))included.add(target.id);return included;}
function visibleTargets(){const ids=branchIds();return (state.replyTargets??[]).filter(t=>!ids||ids.has(t.id));}
function openThread(id){focusedBranches.set(selectedId,id);replyChoices.delete(selectedId);render(state);}
function applyThreadFocus(){
 const anchor=focusedBranches.get(selectedId),ids=branchIds(),bar=document.querySelector('#thread-focus');bar.hidden=!anchor;
 const target=state.replyTargets?.find(t=>t.id===anchor),parent=state.replyTargets?.find(t=>t.id===target?.parent);
 document.querySelector('#focus-label').textContent=target?(parent?'In reply to '+parent.sender+': '+parent.text.replace(/\s+/g,' ').slice(0,75):'Thread · '+target.text.replace(/\s+/g,' ').slice(0,75)):'';
 for(const article of root.querySelectorAll('article'))article.hidden=!!ids&&(!article.id||!ids.has(article.id.slice(6)));
}
document.querySelector('#all-messages').addEventListener('click',()=>{focusedBranches.delete(selectedId);replyChoices.delete(selectedId);render(state);});

function updateReplyContext(){
 const id=chosenReply(),target=state.replyTargets?.find(t=>t.id===id),button=document.querySelector('#reply-context'),subject=document.querySelector('#thread-subject');
 button.textContent=id===null?'New thread · '+(state.selectedThread?.title??''):target?'Replying to '+target.sender+' · '+target.text.replace(/\s+/g,' ').slice(0,90):'Replying in '+(state.selectedThread?.title??'this conversation');
 button.title=target?'Show the message you are replying to':id===null?'Return to replying to the latest message':'';subject.hidden=id!==null;subject.value=subjects.get(selectedId)??'';
 for(const article of root.querySelectorAll('article'))article.classList.toggle('reply-target',article.id==='reply-'+id);drawReplyConnector();
}
const connector=document.createElementNS('http://www.w3.org/2000/svg','svg'),connectorPath=document.createElementNS('http://www.w3.org/2000/svg','path');connector.classList.add('reply-connector');connector.setAttribute('aria-hidden','true');connector.append(connectorPath);document.querySelector('.thread').append(connector);
function drawReplyConnector(){
 const target=document.getElementById('reply-'+chosenReply());if(!target){connectorPath.setAttribute('d','');return;}
 const pane=document.querySelector('.thread').getBoundingClientRect(),messages=root.getBoundingClientRect(),box=document.querySelector('.reply-context-bar').getBoundingClientRect(),source=(target.querySelector('.message-body')??target).getBoundingClientRect();
 const top=Math.max(messages.top+8,Math.min(source.top+12,messages.bottom-8))-pane.top,bottom=box.top+box.height/2-pane.top,x=18,middle=(top+bottom)/2,end=box.left-pane.left-7;
 if(bottom-top<22){connectorPath.setAttribute('d','');return;}
 connector.setAttribute('viewBox',`0 0 ${pane.width} ${pane.height}`);
 const bend=Math.min(16,(bottom-top)*.22),scale=Math.min(1,(bottom-top-2*bend)/32);
 const bezier=(points,t)=>points[0].map((_,axis)=>(1-t)**3*points[0][axis]+3*t*(1-t)**2*points[1][axis]+3*t*t*(1-t)*points[2][axis]+t**3*points[3][axis]);
 const first=[[0,-14],[0,4],[-18,6],[-14,-4]],second=[[-14,-4],[-9,-18],[9,-13],[2,5]],tail=[[2,5],[0,10],[0,12],[0,16]];
 let path=`M 32 ${top+2} C 26 ${top-2} ${x} ${top+3} ${x} ${top+bend} V ${middle-14*scale}`;
 // One narrow loop crosses the straight spine. The underpassing segment has a
 // short gap; it is not an overlaid circle or a line through the composer.
 for(let i=1;i<=100;i++){if(i>=6&&i<=14)continue;const [dx,dy]=bezier(first,i/100);path+=`${i===15?' M':' L'} ${x+dx*scale} ${middle+dy*scale}`;}
 for(let i=1;i<=100;i++){const [dx,dy]=bezier(second,i/100);path+=` L ${x+dx*scale} ${middle+dy*scale}`;}
 for(let i=1;i<=30;i++){const [dx,dy]=bezier(tail,i/30);path+=` L ${x+dx*scale} ${middle+dy*scale}`;}
 path+=` V ${bottom-bend} C ${x} ${bottom-bend*.35} ${x+4} ${bottom-1} ${end} ${bottom-4}`;connectorPath.setAttribute('d',path);
}
root.addEventListener('scroll',drawReplyConnector);window.addEventListener('resize',drawReplyConnector);
render(await(await fetch('/state')).json());

function reactionControls(question,target){
 const choices=[['👍','Thumbs up'],['❤️','Heart'],['🎉','Celebrate'],['👀','Eyes'],['😄','Smile'],['🙏','Thank you']];
 const entry=state.reactionTargets?.find(r=>r.target===target),isQuestion=target===state.questionReplyTarget,mode=entry?.mode??(isQuestion?'protected':'unavailable'),canWithdraw=entry?.canWithdraw??mode==='protected';
 const bar=document.createElement('div');bar.className='reaction-bar';if(isQuestion)bar.id='reaction-count';
 const groups=entry?.groups??(isQuestion?(state.reactionGroups??(state.reactions?[{emoji:'👍',count:state.reactions,mine:state.ownReactions>0}]:[])):[]);
 const react=async(emoji,mine,button)=>{if(mode==='unavailable'||(mine&&!canWithdraw))return;button.disabled=true;try{await post(mine?'/withdraw':'/react',{action:crypto.randomUUID().replaceAll('-',''),token:entry?.token??state.reactionToken,...(entry?{target}:{}),...(mode==='ordinary'?{account:selectedAccount()?.id??''}:{}),...((entry||state.reactionGroups)?{emoji}:{})});}finally{button.disabled=false;}};
 for(const group of groups){const button=document.createElement('button');button.className='reaction-chip';button.dataset.reaction=group.emoji;button.setAttribute('aria-pressed',String(group.mine));const label=choices.find(c=>c[0]===group.emoji)?.[1]??group.emoji;button.title=group.mine?(canWithdraw?'Remove your reaction':'Reaction sent'):'Add your reaction';button.setAttribute('aria-label',`${label}, ${group.count} ${group.count===1?'person':'people'}${group.mine?', including you':''}`);const emoji=document.createElement('span');emoji.textContent=group.emoji;const count=document.createElement('span');count.textContent=String(group.count);button.append(emoji,count);button.addEventListener('click',()=>react(group.emoji,group.mine,button));bar.append(button);}
 const picker=document.createElement('div');picker.className='reaction-picker';picker.hidden=true;picker.setAttribute('role','menu');picker.setAttribute('aria-label','Choose a reaction');
 const add=document.createElement('button');add.className='add-reaction';add.textContent='☺ +';add.title='Add reaction';add.setAttribute('aria-label','Add reaction');add.setAttribute('aria-haspopup','menu');add.setAttribute('aria-expanded','false');if(mode==='unavailable'){add.disabled=true;add.title='Reactions are not available for this message yet';}
 function close(){picker.hidden=true;add.setAttribute('aria-expanded','false');}
 add.addEventListener('click',()=>{const opening=picker.hidden;picker.hidden=!opening;add.setAttribute('aria-expanded',String(opening));if(opening){const room=root.getBoundingClientRect().bottom-question.getBoundingClientRect().top;picker.style.top=room>=85?'28px':'auto';picker.style.bottom=room>=85?'auto':'calc(100% - 20px)';picker.querySelector('button')?.focus();}});
 for(const [emoji,label]of choices){const button=document.createElement('button');button.textContent=emoji;button.setAttribute('role','menuitem');button.setAttribute('aria-label',label);button.title=label;button.disabled=!entry&&!state.reactionGroups&&emoji!=='👍';button.addEventListener('click',()=>{close();const group=groups.find(g=>g.emoji===emoji);if(!group?.mine)react(emoji,false,add);else add.focus();});picker.append(button);}
 picker.addEventListener('keydown',event=>{if(event.key==='Escape'){close();add.focus();}else if(['ArrowLeft','ArrowRight','Home','End'].includes(event.key)){event.preventDefault();const buttons=[...picker.querySelectorAll('button')],index=buttons.indexOf(document.activeElement),next=event.key==='Home'?0:event.key==='End'?buttons.length-1:(index+(event.key==='ArrowRight'?1:-1)+buttons.length)%buttons.length;buttons[next].focus();}});
 bar.addEventListener('focusout',event=>{if(!bar.contains(event.relatedTarget))close();});bar.append(add,picker);question.append(bar);
}

function attachmentCards(){
 for(const file of state.attachments??[]){
  const article=card('Attachment',`${file.state} · resource integrity: ${file.integrity} · ${file.metadata}`,file.name);article.className='attachment';reactionControls(article,file.reactionTarget);
  const description=document.createElement('p');description.textContent=file.description;article.append(description);if(file.state!=='available'){const unavailable=document.createElement('p');unavailable.className='unavailable';unavailable.textContent='Attachment unavailable';article.append(unavailable);}
  const button=document.createElement('button');button.textContent='Download attachment';button.disabled=file.state!=='available';article.append(button);
  button.addEventListener('click',async()=>{button.disabled=true;try{
   const response=await fetch('/download',{method:'POST',headers:{'Content-Type':'application/json','X-Client-Session':state.nonce},body:JSON.stringify({selection:file.selection})});
   if(!response.ok)throw new Error(await response.text());
   const url=URL.createObjectURL(await response.blob()),link=document.createElement('a');link.href=url;link.download='attachment.bin';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
   status.textContent='Attachment downloaded. It was not opened.';
  }catch(error){status.textContent=error.message;}finally{button.disabled=false;}});
 }
}

function richCards(){
 for(const message of state.richMessages??[]){
  const article=card('Alice','Protected rich message',message.text),plain=article.querySelector('.message-body'),container=document.createElement('div'),button=document.createElement('button');button.textContent='Show rich presentation';article.append(button,container);reactionControls(article,message.reactionTarget);let rich=false,request=0;
  button.addEventListener('click',async()=>{const id=++request,generation=renderGeneration;
   if(rich){richController?.dispose();richController=null;container.replaceChildren();plain.hidden=false;rich=false;button.textContent='Show rich presentation';return;}
   button.disabled=true;
   try{const response=await fetch('/rich',{method:'POST',headers:{'Content-Type':'application/json','X-Client-Session':state.nonce},body:JSON.stringify({selection:message.selection})});if(!response.ok)throw Error('Presentation unavailable');const value=await response.json();if(id!==request||generation!==renderGeneration)return;if(value.presentation.state!=='rich')throw Error('Readable text retained; rich presentation unavailable');
    const controller=await mountMessage(container,{tree:value.presentation.tree,images:value.presentation.images},value.configuration);if(id!==request||generation!==renderGeneration){controller.dispose();return;}richController=controller;plain.hidden=true;rich=true;button.textContent='Show plain text';
   }catch(error){status.textContent=error.message;}finally{button.disabled=false;}
  });
 }
}

function ordinaryBody(article,event){
 const source=event.parentText?{id:event.parent,text:event.parentText}:state.legacyQuestion,parents=source?.id&&event.parent===source.id?[source]:[];
 const body=article.querySelector('.message-body');body.replaceChildren();
 for(const block of reconstructQuotes(event.text,parents)){
  if(block.kind==='repeated-quote'){
   const details=document.createElement('details'),summary=document.createElement('summary'),quote=document.createElement('pre');
   details.className='quoted-history';summary.textContent='Quoted text';quote.textContent=block.lines.join('\n');details.append(summary,quote);body.append(details);
  }else body.append(document.createTextNode(block.lines.join('\n')+'\n'));
 }
 const link=document.createElement('a');link.textContent='Download original email';link.href='/original/'+event.id+'.eml';link.download='reply.eml';article.querySelector('.message-details').append(link);
}
