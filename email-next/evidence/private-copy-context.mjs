import {isPrincipalId} from './principal-identifiers.mjs';
// Authenticated context only: outer headers never select a private-copy role.
export function validateDelivery(value){
 if(!value||typeof value!=='object'||Array.isArray(value))return false;
 if(value.kind==='ordinary-v0')return Object.keys(value).length===1;
 return value.kind==='private-copy-v0'&&Object.keys(value).length===3&&
  isPrincipalId(value.originator)&&isPrincipalId(value.recipient)&&value.originator!==value.recipient;
}
export function deliveryMatchesRoster(delivery,principals){
 if(!validateDelivery(delivery)||!Array.isArray(principals)||!principals.length)return false;
 const roster=new Set(principals);
 return delivery.kind==='ordinary-v0'||(roster.size===2&&roster.has(delivery.originator)&&roster.has(delivery.recipient));
}
