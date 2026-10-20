import {evaluateReactions} from './reaction-state.mjs';
import {resolveButtonAnswer} from './button-operations.mjs';
import {resolveEditTargets} from './edit-operation.mjs';
import {validateEnvelopeShape} from './event-envelope.mjs';
import {validateWithdrawalTargets} from './withdrawal-target.mjs';
import {validateSubmissionTarget} from './submission-target.mjs';
const escape=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const label=(text,fallback)=>text===''?fallback:text;
const empty=text=>text===''?'[empty text]':text;
function reference(ref) { return JSON.stringify([ref.principal,ref.event,ref.conversation]); }

// Generates a candidate projection only. No authentication, sending or MIME binding.
export function projectReadable(event, resolveRevision, isPrincipal) {
  if (!validateEnvelopeShape(event,isPrincipal)) return {state:'invalid'};
  const op=event.operation;
  let lines=[];
  if (op.kind==='message' || op.kind==='attachment-message' || op.kind==='rich-message') {
    lines=[op.text];
    if(op.kind==='attachment-message' || (op.kind==='rich-message' && op.attachments.length)) {
      lines.push('', 'Attachments:');
      for(const attachment of op.attachments) {
        const resource=op.manifest.find(item=>item.id===attachment.resource);
        lines.push('- '+label(attachment.name,'Unnamed attachment')+' ['+attachment.mediaType+'; '+resource.size+' bytes]');
        if(attachment.description!=='')lines.push(attachment.description);
        lines.push('Resource: '+resource.id);
      }
      lines.push('Attachment descriptions do not confirm that the files are available or verified.');
    }
    if (op.replyTo.length) lines.push('', 'Reply target: '+reference(op.replyTo[0]));
  } else if (op.kind==='hosted-holder-observation') {
    if(op.target.conversation!==event.conversation)return {state:'invalid-target'};
    const found=resolveRevision(op.target);
    if(!found || found.state==='pending')return {state:'pending'};
    if(found.state!=='valid')return {state:found.state==='conflict'?'conflict':'invalid-target'};
    const target=found.event;
    if(!validateEnvelopeShape(target,isPrincipal) || target.principal!==op.target.principal ||
       target.event!==op.target.event || target.conversation!==op.target.conversation ||
       !event.audience.every(p=>target.audience.includes(p)))return {state:'audience-mismatch'};
    lines=['Reply from a grant holder',op.text,'Observed by: '+event.principal,
      'Hosting service: '+op.service,'Reply target: '+reference(op.target),
      'This does not verify the holder’s mailbox identity.'];
  } else if (op.kind==='service-question') {
    lines=[op.text, '', 'Choices:'];
    for(const [i, option] of op.options.entries()) lines.push(`${i+1}. ${option.label}`);
    lines.push('', 'Proposed answer destination: '+op.serviceAction.service,
      'A compatible configured client is required to submit directly to this service.',
      'An ordinary email reply contacts the sender; it does not confirm that the service recorded an answer.',
      'Opening this message submits nothing.');
  } else if (op.kind==='question') {
    lines=[op.text, '', 'Choices:'];
    for(const [i, option] of op.options.entries()) lines.push(`${i+1}. ${option.label}`);
    lines.push('', 'Reply in your email client to answer. Opening this message submits nothing.');
  } else if (op.kind==='answer') {
    let target;
    const checked=resolveButtonAnswer(event,ref=>{
      const result=resolveRevision(ref);
      if(ref.principal===op.question.principal && ref.event===op.question.event &&
          ref.conversation===op.question.conversation) target=result?.event;
      return result;
    },isPrincipal);
    if(checked.state!=='references-matched') return {state:checked.state};
    // Automatic context copying cannot expand the question's authenticated audience.
    // A separately authorized forwarding/sharing operation is outside this projector.
    if(!validateEnvelopeShape(target,isPrincipal) ||
        !event.audience.every(p=>target.audience.includes(p))) return {state:'audience-mismatch'};
    lines=['Answer: '+checked.answer, 'Question: '+checked.question,
      'Question event: '+reference(op.question)];
    for(const ref of op.replaces) lines.push('Replaces answer: '+reference(ref));
  } else if (op.kind==='reaction' || op.kind==='reaction-withdraw') {
    const own={principal:event.principal,conversation:event.conversation,event:event.event};
    const identity=r=>JSON.stringify([r.principal,r.conversation,r.event]);
    const graph=evaluateReactions(op.target,[own],ref=>{
      if(identity(ref)===identity(own))return {state:'valid',event};
      const found=resolveRevision(ref);
      if(found?.state==='valid' && !validateEnvelopeShape(found.event,isPrincipal))return {state:'invalid'};
      return found;
    },isPrincipal);
    const candidate=graph.results.find(r=>identity(r.ref)===identity(own));
    if(candidate.state!=='valid')return {state:candidate.state};
    lines=op.kind==='reaction'?['Reaction: '+op.emoji,'Target event: '+reference(op.target),
      'This reaction is not an answer or approval.']:['Reaction withdrawal','Target event: '+reference(op.target),
      ...op.reactions.map(ref=>'Withdraws reaction: '+reference(ref)),
      'This does not erase earlier copies or reverse an external action.'];
  } else if (op.kind==='edit') {
    const checked=resolveEditTargets(event,resolveRevision,isPrincipal);
    if(checked.state!=='target-matched') return {state:checked.state};
    lines=['Correction to an earlier message', 'Original message: '+reference(op.root),
      '', 'Replacement text:', empty(op.text)];
    for(const ref of op.predecessors) lines.push('', 'Replaces version: '+reference(ref));
    lines.push('', 'Earlier replies still refer to the versions they originally answered. This correction does not erase earlier copies.');
  } else if (op.kind==='form') {
    lines=[label(op.title,'Untitled form')];
    for (const [index,field] of op.fields.entries()) {
      lines.push('',`${index+1}. ${label(field.label,'Unnamed field')} [${field.type}${field.required?'; required':''}]`);
      for(const [choiceIndex,choice] of (field.choices??[]).entries())
        lines.push(`   ${choiceIndex+1}. ${label(choice.label,'Unnamed choice')}`);
    }
    lines.push('', 'Reply in your email client to answer. Opening this message submits nothing.');
    for(const ref of op.supersedes) lines.push('Revises form event: '+reference(ref));
  } else if (op.kind==='submit') {
    let resolved;
    const checked=validateSubmissionTarget(event,ref=>(resolved=resolveRevision(ref)),isPrincipal);
    if (checked.state!=='target-valid') return {state:checked.state};
    const form=resolved.event.operation;
    const answers=new Map(op.answers.map(a=>[a.field,a.value]));
    lines=['Response to '+label(form.title,'Untitled form'),'Form revision: '+reference(op.revision)];
    for(const [index,field] of form.fields.entries()) {
      lines.push('',`${index+1}. ${label(field.label,'Unnamed field')}`);
      if (!answers.has(field.field)) { lines.push('[unanswered]'); continue; }
      const value=answers.get(field.field);
      if(field.type==='text') lines.push(empty(value));
      else {
        const values=field.type==='single-choice'?[value]:value;
        if(values.length===0) lines.push('[no choices selected]');
        // Definition order supplies a stable readable choice order.
        for(const choice of field.choices.filter(c=>values.includes(c.choice)))
          lines.push('- '+label(choice.label,'Unnamed choice'));
      }
    }
    for(const ref of op.supersedes) lines.push('Replaces response event: '+reference(ref));
  } else if (op.kind==='withdraw') {
    const checked=validateWithdrawalTargets(event,resolveRevision,isPrincipal);
    if(checked.state!=='targets-matched') return {state:checked.state};
    lines=['Withdrawal request for '+label(checked.revision.title,'Untitled form'),
      'Form revision: '+reference(op.revision)];
    for(const ref of op.submissions) lines.push('Response to withdraw: '+reference(ref));
    lines.push('', 'This does not erase the message history or reverse an external action already taken.');
  } else return {state:'unsupported'};
  if(['1','2','3'].includes(event.version) && event.disclosures.length) {
    lines.push('', 'Author-declared external sharing:');
    for(const disclosure of event.disclosures) lines.push(disclosure.kind==='separate-protected-copy'?
      'Planned sharing in a separately protected conversation.':disclosure.kind==='plaintext-email'?
      'Readable email outside the protected conversation.':
      'Provider-hosted bearer access at '+disclosure.service+'.');
    lines.push('This declaration does not prove current availability or prevent later copying.');
  }
  const text=lines.join('\n');
  return {state:'projected',text,html:'<!doctype html><html><head><meta charset="utf-8"></head><body><pre style="white-space:pre-wrap;overflow-wrap:anywhere">'+escape(text)+'</pre></body></html>'};
}
