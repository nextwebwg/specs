# SPDX-FileCopyrightText: 2026 Threadlabs Studio
# SPDX-License-Identifier: MIT
"""Configured encrypted MIME through client-owned actions, not browser automation."""
import unittest
import test_joined_carrier as carrier
from client_flow import ClientFlow
from journal_button_view import derive_button_view
from journal_reaction_view import derive_reaction_view

class CarrierClientActions(unittest.TestCase):
    context_version='3'
    selected_payload='mime-contribution-v0'
    selected_operations=['answer','message','question','reaction','reaction-withdraw']
    setUp=carrier.JoinedCarrier.setUp
    tearDown=carrier.JoinedCarrier.tearDown
    event=carrier.JoinedCarrier.event
    prepare=carrier.JoinedCarrier.prepare
    receive=carrier.JoinedCarrier.receive
    question=carrier.JoinedCarrier.question
    ref=carrier.JoinedCarrier.ref

    def test_client_answer_reaction_withdrawal_and_exact_action_retry(self):
        question=self.question();self.receive(1,self.prepare(0,question));ref=self.ref(question)
        client=ClientFlow(self.senders[1],key=self.devices[1]['key'],
            envelope_sender='bob@example.invalid',recipients=['alice@example.invalid'])
        journal=self.senders[1].receiver.journal
        token=derive_button_view(journal,ref)['sourceToken']
        wire=client.answer('mimeanswer',ref,'c'*32,token,time=self.time)
        self.assertEqual(client.answer('mimeanswer',ref,'c'*32,token,time=self.time),wire)
        self.assertIn('accepted',self.receive(0,wire)[1]['states'].values())
        token=derive_reaction_view(journal,ref)['sourceToken']
        wire=client.react('mimereaction',ref,'👍',token,time=self.time)
        self.assertIn('accepted',self.receive(0,wire)[1]['states'].values())
        token=derive_reaction_view(journal,ref)['sourceToken']
        wire=client.withdraw_reactions('mimewithdraw',ref,token,time=self.time)
        self.assertIn('accepted',self.receive(0,wire)[1]['states'].values())
