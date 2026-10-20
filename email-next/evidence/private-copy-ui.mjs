// Trusted client presentation model comes from accepted carrier context on server.
export function mountPrivateCopy(container,model,reply){
 const title=document.createElement('h2');title.textContent=model.label;
 const notice=document.createElement('p');notice.textContent=model.notice;
 const sharing=document.createElement('p');sharing.textContent=model.sharing;
 const button=document.createElement('button');button.textContent='Reply privately: Friday';
 const result=document.createElement('p');result.setAttribute('role','status');
 button.addEventListener('click',async()=>{button.disabled=true;try{const state=await reply();result.textContent='Private answer delivered. Visible conversation answers: '+state.visibleAnswers+'.';}catch{result.textContent='Private answer held. Try again.';button.disabled=false;}});
 container.replaceChildren(title,notice,sharing,button,result);
}
