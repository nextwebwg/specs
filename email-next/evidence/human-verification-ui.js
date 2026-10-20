'use strict';
const token=location.hash.slice(1);history.replaceState(null,'',location.pathname);
const output=document.querySelector('#result'),form=document.querySelector('form'),entry=document.querySelector('#independent'),check=document.querySelector('#confirmed'),button=document.querySelector('button');
async function request(path,body){const response=await fetch(path,{method:body?'POST':'GET',headers:{'X-Local-Verification':token,...(body?{'Content-Type':'application/json'}:{})},...(body?{body:JSON.stringify(body)}:{})});const value=await response.json();if(!response.ok)throw Error(value.error||'Comparison failed');return value;}
function update(){let valid=false;try{JSON.parse(entry.value);valid=true;}catch{}button.disabled=!valid||!check.checked;}
entry.addEventListener('input',update);check.addEventListener('change',update);
request('/session').then(value=>{document.querySelector('#observed').textContent=JSON.stringify(value.comparison,null,2);document.querySelector('#validity').textContent=value.explanation;}).catch(error=>{output.textContent=error.message;form.hidden=true;});
form.addEventListener('submit',async event=>{event.preventDefault();if(button.disabled)return;button.disabled=true;try{const result=await request('/confirm',{comparison:JSON.parse(entry.value),channel:document.querySelector('#channel').value,independentlyConfirmed:check.checked});output.textContent='Comparison recorded. Human-confirmed correspondent identity; mailbox ownership is not certified.';form.hidden=true;}catch(error){output.textContent=error.message;update();}});
