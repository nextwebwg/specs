"""Legacy navigation projection from trusted parsed, authorized inputs only.

The msg-id checker is the existing narrow fixture spelling, not full RFC5322
parsing. No event/mail association, privacy authorization, ID allocation, MIME
carriage, graph installation or effects are established by this component.
"""
from dataclasses import dataclass
from reaction_mime import _message_id


@dataclass(frozen=True)
class Field:
    state: str = 'absent'
    values: tuple = ()


def _field(value):
    if not isinstance(value,Field) or value.state not in ('absent','invalid','valid') or not isinstance(value.values,tuple):
        raise ValueError('Trusted parsed field required')
    if value.state!='valid' and value.values:raise ValueError('No interpreted values for absent/invalid field')
    if value.state=='valid':
        if not value.values:raise ValueError('Nonempty valid identification field')
        for item in value.values:_message_id(item)
    return value


def project(*, parent=Field(), references=Field(), in_reply_to=Field(),
            disclose_parent=False, disclose_ancestry=False, masked=False,
            max_ids):
    """One already selected parent; caller owns actual parsed provenance/policy.

    max_ids is a local projection count budget; raw header byte/time budgets
    belong to the parser and serializer, not this trusted-input component.
    """
    if any(type(v) is not bool for v in (disclose_parent,disclose_ancestry,masked)) or type(max_ids) is not int or max_ids<1:
        raise ValueError('Explicit flags and positive finite projection budget')
    headers={}
    if masked:return dict(status='legacy-thread-hints-only',headers=headers)
    parent=_field(parent);references=_field(references);in_reply_to=_field(in_reply_to)
    parent_id=parent.values[0] if parent.state=='valid' and len(parent.values)==1 else None
    if parent_id is not None and disclose_parent:headers['In-Reply-To']=parent_id
    if disclose_ancestry:
        # Invalid present References is not absence: never fall back through it.
        if references.state=='valid':chain=references.values
        elif references.state=='absent':
            chain=in_reply_to.values if in_reply_to.state=='valid' and len(in_reply_to.values)==1 else ()
        else:chain=None
        if chain is not None:
            count=len(chain)+(parent_id is not None)
            # No truncation or contiguous allocation before the local count gate.
            if count and count<=max_ids and (parent_id is None or disclose_parent):
                values=chain+((parent_id,) if parent_id is not None else ())
                headers['References']=' '.join(values)
    return dict(status='legacy-thread-hints-only',headers=headers)
