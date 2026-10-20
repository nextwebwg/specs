import {validateMessageShape} from './message-operation.mjs';
import {validateAttachments} from './attachment-metadata.mjs';
export function validateAttachmentMessage(value,isPrincipal) {
 if(!value || typeof value!=='object' || Array.isArray(value) ||
    Object.keys(value).sort().join(',')!=='attachments,kind,manifest,replyTo,text' ||
    value.kind!=='attachment-message')return false;
 if(!validateMessageShape({kind:'message',text:value.text,replyTo:value.replyTo},isPrincipal) ||
    !validateAttachments(value.attachments,value.manifest))return false;
 // This operation has no embedded-body resources: every resource is an attachment.
 return value.attachments.length>0 && value.attachments.length===value.manifest.length;
}
