"""Real expired-leaf comparison with a locally issued two-member fixture.

This exercises only MLS reception, not current-suite signed admission, current
account authority, an issuance journal, durable key custody or platform erasure.
"""
import os
from pathlib import Path
import time
import unittest

from mls_receive import worker_call
from provider_mls import call


class DelayedWelcomeProbeTests(unittest.TestCase):
    def test_real_expiry_distinguishes_receiving_creation_and_consumption(self):
        binary = Path(os.environ['EMAIL_NEXT_MLS_BIN_DIR']) / 'delayed-welcome-probe'
        fixture = call(binary, op='fixture')
        # The fixture constructs and validates the package, Welcome and first
        # ciphertext before this actual clock boundary. No source clock changes.
        wait = fixture['sendUntil'] + 1 - time.time()
        if wait > 0:
            time.sleep(wait)
        strict = worker_call(binary, dict(fixture, op='strict'))
        self.assertEqual(strict.get('status'), 'worker-rejected')
        self.assertEqual(strict.get('reason'), 'stage')
        expired = worker_call(binary, dict(fixture, op='delayed', receiveUntil=int(time.time()) - 1))
        self.assertEqual(expired.get('reason'), 'receive-window')
        wrong = worker_call(binary, dict(fixture, op='delayed', reference='0' * 64))
        self.assertEqual(wrong.get('reason'), 'reference')
        accepted = call(binary, **dict(fixture, op='delayed'))
        self.assertTrue(accepted['packageConsumed'])
        received = call(binary.with_name('receive-staged'), format='openmls-0.9.1-map-0', checkpoint=accepted['checkpoint'], group=fixture['group'], wire=fixture['wire'])
        self.assertEqual(bytes.fromhex(received['application']), b'An already-created encrypted message')
        self.assertEqual(received['processed']['credential'], fixture['owner'])
        repeated = worker_call(binary, dict(fixture, op='delayed', checkpoint=accepted['checkpoint']))
        self.assertEqual(repeated.get('reason'), 'missing-owned-package')
        # The ordinary validator still rejects using this expired publication
        # for a new outgoing addition. No sending validator is changed here.
        from passive_discovery_package import validate_package
        result = validate_package(bytes.fromhex(fixture['package']), principal='enp0:' + '03' * 32, device='end0:' + '04' * 32, accepted_signing_key=bytes.fromhex(fixture['key']), earliest=str(int(time.time())), latest=str(int(time.time())), executable=binary.with_name('validate-discovery-package'))
        self.assertNotEqual(result, {'status': 'package-valid'})


if __name__ == '__main__':
    unittest.main()
