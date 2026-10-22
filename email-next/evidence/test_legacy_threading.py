import unittest
from legacy_threading import Field,project

A='<a@example.invalid>'
B='<b@example.invalid>'
C='<c@example.invalid>'
valid=lambda *values:Field('valid',values)


class LegacyThreadProjection(unittest.TestCase):
    def emit(self,**kwargs):
        return project(**(dict(parent=valid(B),disclose_parent=True,disclose_ancestry=True,max_ids=10)|kwargs))['headers']

    def test_one_parent_chain_preserves_values_order_and_duplicates(self):
        self.assertEqual(self.emit(references=valid(A)),{'In-Reply-To':B,'References':A+' '+B})
        self.assertEqual(self.emit(references=valid(A,A)),{'In-Reply-To':B,'References':A+' '+A+' '+B})
        self.assertEqual(self.emit(references=valid('<MiXeD@example.invalid>')),{'In-Reply-To':B,'References':'<MiXeD@example.invalid> '+B})

    def test_absent_references_uses_only_single_in_reply_to(self):
        self.assertEqual(self.emit(in_reply_to=valid(A))['References'],A+' '+B)
        self.assertEqual(self.emit(in_reply_to=valid(A,C))['References'],B)
        self.assertEqual(self.emit(in_reply_to=Field('invalid'))['References'],B)

    def test_invalid_present_references_is_not_absence(self):
        self.assertEqual(self.emit(references=Field('invalid'),in_reply_to=valid(A)),{'In-Reply-To':B})

    def test_missing_or_ambiguous_message_id_does_not_erase_valid_ancestry(self):
        for parent in (Field(),Field('invalid'),valid(B,C)):
            with self.subTest(parent=parent):
                self.assertEqual(self.emit(parent=parent,references=valid(A)),{'References':A})
                self.assertEqual(self.emit(parent=parent,in_reply_to=valid(A)),{'References':A})
        self.assertEqual(self.emit(parent=Field()),{})

    def test_privacy_and_complete_budget_precede_reference_emission(self):
        self.assertEqual(self.emit(references=valid(A),disclose_ancestry=False),{'In-Reply-To':B})
        self.assertEqual(self.emit(references=valid(A),disclose_parent=False),{})
        self.assertEqual(self.emit(references=valid(A),max_ids=1),{'In-Reply-To':B})
        self.assertEqual(self.emit(references=valid(A),max_ids=2)['References'],A+' '+B)
        # Masked projection does not inspect/release an otherwise unused chain.
        self.assertEqual(self.emit(masked=True,references='unparsed-private-data'),{})

    def test_invalid_trusted_input_is_not_a_parser_or_policy_override(self):
        for change in (dict(max_ids=0),dict(max_ids=True),dict(masked='yes'),dict(parent=valid('<bad\r\nBcc: x@y>')),dict(references=Field('absent',(A,))),dict(parent={'state':'valid','values':[A]})):
            with self.subTest(change=change),self.assertRaises(ValueError):self.emit(**change)
        self.assertEqual(project(max_ids=10)['status'],'legacy-thread-hints-only')


if __name__=='__main__':unittest.main()
