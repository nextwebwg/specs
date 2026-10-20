"""Generated correction MIME round trip; no authenticated receiver or SMTP."""
import json
from pathlib import Path
import subprocess
import unittest
from email import policy
from email.parser import BytesParser
from event_encoding import encode_event, decode_event
from mime_package import contribution_alternatives, EVENT_MEDIA_TYPE

HERE=Path(__file__).resolve().parent
class EditMimeTests(unittest.TestCase):
    def fixture(self):
        ref={'principal':'enp0:'+'a'*64,'conversation':'2'*32,'event':'3'*32}
        event={'version':'0','purpose':'contribution','event':'1'*32,
               'conversation':ref['conversation'],'principal':ref['principal'],
               'audience':[ref['principal'],'enp0:'+'b'*64],
               'operation':{'kind':'edit','root':ref,'predecessors':[ref],'text':'Meet at 4 / 明日'}}
        root={**ref,'operation':{'kind':'message','text':'Earlier private text','replyTo':[]}}
        script="""import {projectReadable} from './readable-projection.mjs';
import {isPrincipalId} from './principal-identifiers.mjs';
let data='';for await(const chunk of process.stdin)data+=chunk;
const {event,root}=JSON.parse(data);
process.stdout.write(JSON.stringify(projectReadable(event,()=>({state:'valid',event:root}),isPrincipalId)));
"""
        projection=json.loads(subprocess.run(['node','--input-type=module','-e',script],
          cwd=HERE,input=json.dumps({'event':event,'root':root}),text=True,capture_output=True,check=True).stdout)
        self.assertEqual(projection['state'],'projected')
        return event,projection

    def test_generated_correction_preserves_bytes_and_readable_alternatives(self):
        event,projection=self.fixture()
        original=encode_event(event)
        wire=contribution_alternatives(original,projection['text'],projection['html']).as_bytes()
        message=BytesParser(policy=policy.default).parsebytes(wire)
        self.assertFalse(message.defects)
        plain,html,structured=list(message.iter_parts())
        self.assertEqual([p.get_content_type() for p in [plain,html,structured]],['text/plain','text/html',EVENT_MEDIA_TYPE])
        self.assertEqual(decode_event(structured.get_payload(decode=True))['octets'],original)
        for part in [plain,html]:
            text=part.get_content()
            self.assertIn('Meet at 4 / 明日',text)
            self.assertIn(event['operation']['root']['event'],text)
            self.assertNotIn('Earlier private text',text)

    def test_packager_does_not_claim_to_validate_fallback_binding(self):
        event,_=self.fixture()
        message=contribution_alternatives(encode_event(event),'Unrelated fallback','<p>Unrelated</p>')
        self.assertIn('Unrelated',next(message.iter_parts()).get_content())
        # Sender projection validation and receiver authenticated binding remain
        # separate required stages; MIME construction alone provides neither.

class IncomingEditMimeTests(unittest.TestCase):
    fixture = EditMimeTests.fixture
    def inspect(self,wire,**limits):
        from mime_package import inspect_contribution_package
        return inspect_contribution_package(wire,**{'max_wire_bytes':16384,'max_parts':4,'max_decoded_bytes':8192,**limits})

    def package(self):
        event,projection=self.fixture()
        return contribution_alternatives(encode_event(event),projection['text'],projection['html'])

    def test_strict_selection_retains_exact_event_bytes(self):
        package=self.package()
        selected=self.inspect(package.as_bytes())
        self.assertEqual(selected['event']['octets'],list(package.iter_parts())[2].get_payload(decode=True))
        self.assertIn(b'Correction',selected['plain'])

    def test_duplicate_or_reordered_alternatives_fail(self):
        for mode in ['duplicate','reverse']:
            package=self.package();parts=list(package.iter_parts())
            package.set_payload(parts+[parts[2]] if mode=='duplicate' else list(reversed(parts)))
            with self.assertRaises(ValueError):self.inspect(package.as_bytes(),max_parts=10)

    def test_event_parameters_and_transfer_corruption_fail(self):
        for mode in ['parameter','base64','encoding']:
            package=self.package();part=list(package.iter_parts())[2]
            if mode=='parameter':part.set_param('version','0')
            elif mode=='base64':part.set_payload('not!base64')
            else:part.replace_header('Content-Transfer-Encoding','8bit')
            with self.assertRaises(ValueError):self.inspect(package.as_bytes())

    def test_wire_part_and_decoded_budgets_fail_without_partial_return(self):
        wire=self.package().as_bytes()
        for limits in [{'max_wire_bytes':len(wire)-1},{'max_parts':3},{'max_decoded_bytes':1}]:
            with self.assertRaises(ValueError):self.inspect(wire,**limits)
