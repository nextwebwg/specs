"""Record/destination checks only; no envelope negotiation, UI or delivery proof."""
import copy
import unittest
from event_encoding import encode_event
from reply_intent import inspect_record, destination, validate, TARGETS, NON_TARGETS

A, B, C, D = ['enp0:' + x*64 for x in 'abcd']


def record(kind='discussion', private=True):
    result = dict(version='0', kind=kind)
    if kind == 'discussion':
        result.update(participants=[A, B], privateReplies=private)
    return result


class ReplyIntentTests(unittest.TestCase):
    def check(self, value, operation='message', author=A, audience=None):
        return validate(value, operation=operation, author=author,
                        audience=[A, B, C] if audience is None else audience)

    def choose(self, value, actor=B, action='discussion', author=A, audience=None):
        return destination(value, operation='message', author=author,
                           audience=[A, B, C] if audience is None else audience,
                           actor=actor, action=action)

    def test_discussion_set_excludes_copied_observer_and_has_no_implicit_fanout(self):
        self.assertEqual(self.choose(record()), [A, B])
        with self.assertRaises(ValueError):
            self.choose(record(), actor=C)
        self.assertEqual(self.choose(record(), actor=C, action='private'), [A, C])

    def test_private_switch_can_disable_private_response_for_every_reader(self):
        for who in [A, B, C]:
            with self.subTest(who=who), self.assertRaises(ValueError):
                self.choose(record(private=False), actor=who, action='private')
        self.assertEqual(self.choose(record(private=False)), [A, B])

    def test_none_disables_both_actions_and_private_disables_discussion(self):
        for action in ['discussion', 'private']:
            with self.subTest(action=action), self.assertRaises(ValueError):
                self.choose(record('none'), action=action)
        with self.assertRaises(ValueError):
            self.choose(record('private'))
        self.assertEqual(self.choose(record('private'), action='private'), [A, B])

    def test_continuation_uses_actual_author_instead_of_original_announcement_author(self):
        self.assertEqual(self.choose(record('private'), action='private'), [A, B])
        self.assertEqual(self.choose(record('private'), actor=A, author=B,
                                     audience=[A, B], action='private'), [A, B])

    def test_each_operation_has_exact_applicability_without_disabling_its_own_effect(self):
        for operation in TARGETS:
            for kind in ['discussion', 'private', 'none']:
                self.check(record(kind), operation)
            with self.subTest(operation=operation), self.assertRaises(ValueError):
                self.check(record('not-applicable'), operation)
        for operation in NON_TARGETS:
            self.check(record('not-applicable'), operation)
            for kind in ['discussion', 'private', 'none']:
                with self.subTest(operation=operation, kind=kind), self.assertRaises(ValueError):
                    self.check(record(kind), operation)
        with self.assertRaises(ValueError):
            self.check(record(), 'unknown-operation')

    def test_foreign_actor_or_changed_account_cannot_inherit_discussion_permission(self):
        for who in [C, D]:
            with self.subTest(who=who), self.assertRaises(ValueError):
                self.choose(record(), actor=who)
        with self.assertRaises(ValueError):
            self.choose(record('private'), actor=D, action='private')

    def test_incorrect_shape_version_type_and_duplicate_decoded_members(self):
        bad = [None, [], {}, dict(version='1', kind='none'),
               dict(version='0', kind='none', participants=[]),
               dict(version='0', kind='private', recipient=D),
               dict(version='0', kind='future')]
        for value in ['true', 'false', 0, 1, None]:
            r = record(); r['privateReplies'] = value; bad.append(r)
        for key in record():
            r = record(); del r[key]; bad.append(r)
        for r in bad:
            with self.subTest(record=r), self.assertRaises(ValueError):
                self.check(r)
        for raw in [b'{"version":"0","kind":"none","k\\u0069nd":"private"}',
                    b'{"version":"0","kind":null}',
                    b'{"version":0,"kind":"none"}']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                inspect_record(raw, operation='message', author=A, audience=[A, B])

    def test_participant_order_omission_outside_and_invalid_id_rejected(self):
        for people in [[], [B], [B, A], [A, B, B], [A, D], [A, 'enp0:'+'0'*64], [A, 'bob']]:
            r = record(); r['participants'] = people
            with self.subTest(people=people), self.assertRaises(ValueError):
                self.check(r)
        for audience in [[], [B, C], [A, B, B], [A, 'bob']]:
            with self.subTest(audience=audience), self.assertRaises(ValueError):
                self.check(record(), audience=audience)

    def test_exact_source_bytes_and_inputs_preserved(self):
        raw = b'{ "kind" : "none", "version" : "0" }'
        candidate = inspect_record(raw, operation='message', author=A, audience=[A, B])
        self.assertEqual(candidate['octets'], raw)
        self.assertEqual(candidate['state'], 'candidate-reply-intent')
        self.assertNotEqual(encode_event(candidate['record']), raw)
        r = record(); before = copy.deepcopy(r)
        result = self.choose(r); result.append(D)
        self.assertEqual(r, before)

    def test_self_contact_has_one_principal_and_unknown_action_never_defaults(self):
        self.assertEqual(self.choose(record('private'), actor=A, action='private',
                                     audience=[A]), [A])
        for action in ['', 'reply-all', None]:
            with self.subTest(action=action), self.assertRaises(ValueError):
                self.choose(record(), action=action)


if __name__ == '__main__':
    unittest.main()
