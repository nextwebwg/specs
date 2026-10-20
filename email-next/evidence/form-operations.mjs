import {isObjectId, isEventReference} from './event-identifiers.mjs';

function shape(value, names) {
  return value !== null && typeof value === 'object' && !Array.isArray(value) &&
    Object.keys(value).length === names.length && names.every(name=>Object.hasOwn(value,name));
}
function unique(items, key) {
  return new Set(items.map(key)).size === items.length;
}
function scalarText(value) {
  if (typeof value !== 'string') return false;
  for (const char of value) {
    const point=char.codePointAt(0);
    if (point>=0xd800 && point<=0xdfff) return false;
  }
  return true;
}
function field(value) {
  const base=['field','label','type','required'];
  if (!value || !isObjectId(value.field) || !scalarText(value.label) || typeof value.required!=='boolean') return false;
  if (value.type==='text') return shape(value,base);
  if (!['single-choice','multiple-choice'].includes(value.type) || !shape(value,[...base,'choices'])) return false;
  return Array.isArray(value.choices) && value.choices.length>0 &&
    value.choices.every(c=>shape(c,['choice','label']) && isObjectId(c.choice) && scalarText(c.label)) &&
    unique(value.choices,c=>c.choice);
}
function references(values, isPrincipal, nonempty=false) {
  return Array.isArray(values) && (!nonempty || values.length>0) &&
    values.every(ref=>isEventReference(ref,isPrincipal)) &&
    unique(values,ref=>JSON.stringify([ref.principal,ref.event,ref.conversation]));
}
// Shape only: no authority, graph, reference resolution, or field-value membership check.
export function validateOperationShape(value, isPrincipal) {
  if (!value || !isObjectId(value.form)) return false;
  if (value.kind==='form') {
    return shape(value,['kind','form','title','fields','supersedes']) && scalarText(value.title) &&
      Array.isArray(value.fields) && value.fields.every(field) && unique(value.fields,f=>f.field) &&
      references(value.supersedes,isPrincipal);
  }
  if (value.kind==='submit') {
    return shape(value,['kind','form','revision','answers','supersedes']) &&
      isEventReference(value.revision,isPrincipal) && references(value.supersedes,isPrincipal) &&
      Array.isArray(value.answers) && value.answers.every(a=>shape(a,['field','value']) && isObjectId(a.field) &&
        (scalarText(a.value) || (Array.isArray(a.value) && a.value.every(isObjectId) && unique(a.value,x=>x)))) &&
      unique(value.answers,a=>a.field);
  }
  if (value.kind==='withdraw') {
    return shape(value,['kind','form','revision','submissions']) && isEventReference(value.revision,isPrincipal) &&
      references(value.submissions,isPrincipal,true);
  }
  return false;
}
