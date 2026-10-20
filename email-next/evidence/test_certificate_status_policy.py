"""Synthetic policy boundaries plus actual same-socket TLS marker gating."""
import dataclasses
import hashlib
import socket
import ssl
import threading
import unittest
from certificate_status_policy import Observation, decide, send_fixture_probe, MAX_AGE
from service_tls import wrap_service_socket
import test_service_tls as tls_fixtures

class StatusPolicyTests(unittest.TestCase):
    def observation(self, **changes):
        base=Observation('fixture-peer','revision-1',2000000,'good',999900,999900,1001000)
        return dataclasses.replace(base,**changes)

    def check(self, observation=None, **changes):
        args=dict(now=1000000,credible_clock=True,mode='fresh-status-required',policy_revision='revision-1')
        args.update(changes)
        return decide(observation or self.observation(),**args)

    def test_time_boundaries(self):
        for changes,expected in [({'next_update':1000000},False),({'next_update':1000001},True),
            ({'this_update':1000000-MAX_AGE,'next_update':None},True),
            ({'this_update':999999-MAX_AGE,'next_update':None},False),
            ({'this_update':1000300},True),({'this_update':1000301},False),
            ({'produced_at':1000300},True),({'produced_at':1000301},False)]:
            with self.subTest(changes=changes):self.assertEqual(self.check(self.observation(**changes)).permitted,expected)

    def test_modes_and_staples(self):
        for mode in ('web-compatible','fresh-status-required'):
            for status in ('unknown','unavailable','invalid'):
                with self.subTest(mode=mode,status=status):
                    r=self.check(self.observation(status=status),mode=mode)
                    self.assertEqual(r.permitted,mode=='web-compatible')
                    if r.permitted:self.assertEqual(r.status,'indeterminate')
                    self.assertFalse(self.check(self.observation(status=status,staple_present=True),mode=mode).permitted)
            self.assertFalse(self.check(self.observation(status='revoked'),mode=mode).permitted)
            self.assertFalse(self.check(credible_clock=False,mode=mode).permitted)
            self.assertFalse(self.check(self.observation(staple_required=True),mode=mode).permitted)
            self.assertFalse(self.check(self.observation(staple_required=True,staple_present=True),resumed=True,mode=mode).permitted)
            self.assertFalse(self.check(self.observation(next_update=1000000,staple_present=True),mode=mode).permitted)

    def test_exceptions_nonce_and_policy(self):
        self.assertTrue(self.check(self.observation(exception='valid',status='unavailable')).permitted)
        self.assertFalse(self.check(self.observation(exception='invalid')).permitted)
        self.assertFalse(self.check(policy_revision='new').permitted)
        self.assertFalse(self.check(self.observation(certificate_expiry=1000000)).permitted)
        self.assertFalse(self.check(self.observation(nonce='mismatch')).permitted)
        for nonce in ('match','omitted','not-requested'):
            self.assertTrue(self.check(self.observation(nonce=nonce)).permitted)
        for key,value in [('now',True),('max_age',True),('max_age',MAX_AGE+1),('future_skew',301)]:
            with self.assertRaises(ValueError):self.check(**{key:value})

    def test_reuse_expiry(self):
        o=self.observation(next_update=1000001)
        self.assertTrue(self.check(o,resumed=True).permitted)
        self.assertFalse(self.check(o,now=1000001,resumed=True).permitted)

class SameConnectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):tls_fixtures.ServiceTLSTest.setUpClass()
    @classmethod
    def tearDownClass(cls):tls_fixtures.ServiceTLSTest.tearDownClass()

    def run_probe(self, status, mode, *, wrong_peer=False, credible_clock=True):
        cert,key=tls_fixtures.ServiceTLSTest().leaf('api.service.example')
        context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version=ssl.TLSVersion.TLSv1_3
        context.load_cert_chain(cert,key)
        observed=[];errors=[]
        with socket.socket() as listener:
            listener.bind(('127.0.0.1',0));listener.listen(1);listener.settimeout(4)
            def serve():
                try:
                    with listener.accept()[0] as raw:
                        raw.settimeout(4)
                        with context.wrap_socket(raw,server_side=True) as tls:
                            observed.append(tls.recv(100))
                            tls.unwrap()
                except Exception as error:errors.append(error)
            thread=threading.Thread(target=serve);thread.start()
            try:
                with socket.create_connection(listener.getsockname(),timeout=4) as raw:
                    with wrap_service_socket(raw,reference_host='api.service.example',trusted_ca_file=str(tls_fixtures.ServiceTLSTest.ca_file)) as tls:
                        import time
                        now=int(time.time())
                        digest=hashlib.sha256(tls.getpeercert(binary_form=True)).hexdigest()
                        o=Observation('wrong' if wrong_peer else digest,'r1',now+100,status,now-10,now-10,now+50)
                        result=send_fixture_probe(tls,o,now=now,credible_clock=credible_clock,mode=mode,policy_revision='r1')
                        tls.unwrap()
            finally:thread.join(5)
            self.assertFalse(thread.is_alive());self.assertEqual(errors,[])
            self.assertEqual(observed,[b'STATUS-POLICY-PROBE' if result.permitted else b''])
            return result

    def test_actual_socket_gate(self):
        for status,mode,expected in [('good','fresh-status-required',True),('revoked','web-compatible',False),
            ('unknown','fresh-status-required',False),('unknown','web-compatible',True)]:
            with self.subTest(status=status,mode=mode):self.assertEqual(self.run_probe(status,mode).permitted,expected)
        self.assertFalse(self.run_probe('good','fresh-status-required',wrong_peer=True).permitted)
        self.assertFalse(self.run_probe('good','web-compatible',credible_clock=False).permitted)

if __name__=='__main__':unittest.main()
