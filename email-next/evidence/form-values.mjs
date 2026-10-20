import {isObjectId} from './event-identifiers.mjs';
// Input form is an already validated exact revision. This is not an authority check.
export function validateAnswers(answers, fields) {
  if (!Array.isArray(answers)) return false;
  const definitions=new Map(fields.map(field=>[field.field,field]));
  const seen=new Set();
  for (const answer of answers) {
    if (!answer || typeof answer!=='object' || Array.isArray(answer)) return false;
    const keys=Object.keys(answer).sort();
    if (keys.length!==2 || keys[0]!=='field' || keys[1]!=='value' ||
        !isObjectId(answer.field) || seen.has(answer.field)) return false;
    seen.add(answer.field);
    const definition=definitions.get(answer.field);
    if (!definition) return false;
    const value=answer.value;
    if (definition.type==='text') {
      if (typeof value!=='string') return false;
    } else if (definition.type==='single-choice') {
      if (!isObjectId(value) || !definition.choices.some(c=>c.choice===value)) return false;
    } else if (definition.type==='multiple-choice') {
      if (!Array.isArray(value) || new Set(value).size!==value.length ||
          !value.every(v=>isObjectId(v)&&definition.choices.some(c=>c.choice===v))) return false;
    } else return false;
  }
  return fields.every(field=>!field.required || seen.has(field.field));
}
