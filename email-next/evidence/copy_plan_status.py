"""Pure local outcome projection from trusted normalized per-copy evidence.

No identity, audience, disclosure, policy, crypto, journal or transport validation.
Candidate units are inspection results, never permission to send or retry.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class RecipientEvidence:
    recipient: str
    accepted: bool = False
    uncertain: bool = False
    failed: bool = False
    in_flight: bool = False
    conflicted: bool = False


@dataclass(frozen=True)
class CopySnapshot:
    copy: str
    readiness: str
    recipients: tuple
    content_exposed: bool = False
    content_release_uncertain: bool = False


def summarize(planned, copies, *, progression, collective_activated=False, complete=True):
    if progression not in ('independent','together') or type(collective_activated) is not bool or type(complete) is not bool:
        raise ValueError('Explicit local progression/snapshot state required')
    if progression == 'independent' and collective_activated:
        raise ValueError('No collective barrier in independent mode')
    if type(planned) is not tuple or not planned or any(type(x) is not str or not x for x in planned) or len(set(planned)) != len(planned):
        raise ValueError('Complete frozen planned-copy inventory required')
    if type(copies) not in (list,tuple):
        raise ValueError('Copy snapshots required')
    seen=set(); units=[]; candidates=[]; exposed=False; release_uncertain=False
    counts={key:0 for key in ('accepted','uncertain','failed','in_flight','conflicted','pending')}
    for copy in copies:
        if type(copy) is not CopySnapshot or type(copy.copy) is not str or copy.copy not in planned or copy.copy in seen:
            raise ValueError('Exact unique planned copy snapshot required')
        if copy.readiness not in ('waiting','held','retiring','ready') or type(copy.content_exposed) is not bool or type(copy.content_release_uncertain) is not bool or type(copy.recipients) is not tuple or not copy.recipients:
            raise ValueError('Bounded complete nonempty recipient snapshot required')
        seen.add(copy.copy);exposed |= copy.content_exposed;release_uncertain |= copy.content_release_uncertain;recipients=set()
        for recipient in copy.recipients:
            if type(recipient) is not RecipientEvidence or type(recipient.recipient) is not str or not recipient.recipient or recipient.recipient in recipients:
                raise ValueError('Unique copy-scoped recipient evidence required')
            recipients.add(recipient.recipient)
            facts=[getattr(recipient,key) for key in ('accepted','uncertain','failed','in_flight','conflicted')]
            if any(type(v) is not bool for v in facts):
                raise ValueError('Exact Boolean observations required')
            units.append((copy.copy,recipient))
            for key in counts:
                if key != 'pending':counts[key] += int(getattr(recipient,key))
            if not any(facts):
                counts['pending'] += 1
                if copy.readiness == 'ready':candidates.append((copy.copy,recipient.recipient))
    complete = complete and seen == set(planned)
    reason = 'complete' if complete else 'incomplete-snapshot'
    if progression == 'together' and not collective_activated:
        if exposed or release_uncertain or any(counts[k] for k in counts if k != 'pending'):
            # Existing external/attempt observations cannot be erased by an
            # absent or unreconciled local activation record after restart.
            complete=False;reason='collective-state-unreconciled'
        if any(copy.readiness != 'ready' for copy in copies):candidates=[]
    if not complete:candidates=[]
    all_handoffs = (complete and not release_uncertain and len(units)>0 and counts['accepted']==len(units) and
                    not any(counts[k] for k in ('uncertain','failed','in_flight','conflicted','pending')))
    return dict(complete=complete,reason=reason,counts=counts,
                all_handoffs_confirmed=all_handoffs,content_exposure_observed=exposed,
                content_release_uncertain=release_uncertain,content_may_be_exposed=exposed or release_uncertain,
                candidate_units=tuple(sorted(candidates)))
