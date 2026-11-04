"""Timing-only decisions for the proposed current-suite receive window.

Local issuance records are trusted custody metadata. Peer deadlines never extend
these records. This module grants no identity, package, membership or send right;
all original signatures, crypto, current authority and selection checks remain.
Historical encodings do not acquire this policy by calling this helper.
"""
import re

MAX = 2**64 - 1
DEFAULT_RECEIVE_DELAY = 604800
FIELDS = {'version', 'purpose', 'keyPackageRef', 'notBefore', 'sendUntil', 'receiveUntil'}


def uint(value):
    if not isinstance(value, str) or not re.fullmatch(r'0|[1-9][0-9]*', value) or int(value) > MAX:
        raise ValueError('Canonical uint64 required')
    return int(value)


def validate(record):
    if not isinstance(record, dict) or set(record) != FIELDS or record['version'] != '0' or record['purpose'] != 'admission-window':
        raise ValueError('Exact local admission window required')
    if not isinstance(record['keyPackageRef'], str) or not re.fullmatch('[0-9a-f]{64}', record['keyPackageRef']):
        raise ValueError('Exact package reference required')
    start, send, receive = (uint(record[k]) for k in ('notBefore', 'sendUntil', 'receiveUntil'))
    if not start <= send <= receive:
        raise ValueError('Ordered admission window required')
    return start, send, receive


def issue(reference, not_before, not_after, *, receive_delay=DEFAULT_RECEIVE_DELAY):
    if type(receive_delay) is not int or not 0 <= receive_delay <= MAX:
        raise ValueError('Trusted receive-delay policy required')
    end = uint(not_after)
    if receive_delay > MAX - end:
        raise ValueError('Receive deadline overflow')
    record = dict(version='0', purpose='admission-window', keyPackageRef=reference, notBefore=not_before, sendUntil=not_after, receiveUntil=str(end + receive_delay))
    validate(record)
    return record


def clock(time):
    if not isinstance(time, dict) or set(time) != {'earliest', 'latest'}:
        raise ValueError('Credible interval required')
    lo, hi = uint(time['earliest']), uint(time['latest'])
    if lo > hi:
        raise ValueError('Ordered credible interval required')
    return lo, hi


def check_create_window(local, time):
    start, send, _ = validate(local)
    lo, hi = clock(time)
    return 'within-create-window' if start <= lo <= hi <= send else 'creation-held'


def check_receive_window(local, invitation, time):
    start, send, retained = validate(local)
    if not isinstance(invitation, dict) or set(invitation) != {'keyPackageRef', 'notBefore', 'notAfter', 'receiveUntil'}:
        raise ValueError('Exact selected invitation interval required')
    if invitation['keyPackageRef'] != local['keyPackageRef']:
        raise ValueError('Exact locally retained package required')
    before, after, deadline = (uint(invitation[k]) for k in ('notBefore', 'notAfter', 'receiveUntil'))
    if not start <= before <= after <= send or not after <= deadline <= retained:
        raise ValueError('Invitation exceeds original custody window')
    lo, hi = clock(time)
    if not before <= lo <= hi <= deadline:
        return 'receiving-held'
    return 'within-receive-window' if hi <= after else 'within-delayed-receive-window'
