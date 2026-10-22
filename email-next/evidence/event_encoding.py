"""Experimental event decoder, with byte/depth bounds; not a production or schema parser."""
import json

MAX_EVENT_OCTETS = 1048576
MAX_CONTAINER_DEPTH = 32

class EventLimitExceeded(ValueError):
    """Incomplete processing under the profile limits, not maliciousness evidence."""

def check_limits(data, *, max_octets=MAX_EVENT_OCTETS):
    if len(data) > max_octets:
        raise EventLimitExceeded('Event byte limit exceeded')
    depth = 0
    quoted = False
    escaped = False
    # JSON structural bytes are ASCII and cannot occur inside UTF-8 multibyte bytes.
    # Syntax validation still belongs to the JSON parser after this bounded scan.
    for byte in data:
        if quoted:
            if escaped:
                escaped = False
            elif byte == 92:
                escaped = True
            elif byte == 34:
                quoted = False
        elif byte == 34:
            quoted = True
        elif byte in (91, 123):
            depth += 1
            if depth > MAX_CONTAINER_DEPTH:
                raise EventLimitExceeded('Event nesting limit exceeded')
        elif byte in (93, 125):
            depth -= 1
            if depth < 0:
                raise ValueError('Unmatched closing container')

def decode_event(data, *, max_octets=MAX_EVENT_OCTETS, nullable_members=()):
    if not isinstance(data, bytes):
        raise TypeError('Expected exact bytes')
    check_limits(data, max_octets=max_octets)
    if data.startswith(b'\xef\xbb\xbf'):
        raise ValueError('BOM is not permitted')
    text = data.decode('utf-8', errors='strict')
    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate member')
            result[key] = value
        return result
    def reject_number(value):
        raise ValueError('Numbers are not permitted')
    parsed = json.loads(text, object_pairs_hook=object_pairs,
                        parse_int=reject_number, parse_float=reject_number,
                        parse_constant=reject_number)
    def validate(value, path=()):
        # Opt-in applies only to explicitly named root fields of an owning schema.
        # Historical event callers retain their null rejection.
        if value is None and len(path) == 1 and path[0] in nullable_members:
            return
        if isinstance(value, str):
            if any(0xD800 <= ord(c) <= 0xDFFF for c in value):
                raise ValueError('Lone surrogate')
        elif isinstance(value, bool):
            pass
        elif isinstance(value, dict):
            for key, item in value.items():
                validate(key)
                validate(item, path + (key,))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                validate(item, path + (index,))
        else:
            raise ValueError('Unsupported value')
    if not isinstance(parsed, dict):
        raise ValueError('Event root must be an object')
    validate(parsed)
    return {'octets': data, 'value': parsed}

def serialize_json(value):
    """Shared exact JSON serializer, including string measurement for hosted admission."""
    text = json.dumps(value, ensure_ascii=False, allow_nan=False,
                      separators=(',', ':')).replace('/', '\\/')
    return text.encode('utf-8', errors='strict')

def encode_event(value, *, nullable_members=()):
    """Serialize once; callers retain returned bytes for retries."""
    data = serialize_json(value)
    decode_event(data, nullable_members=nullable_members)
    return data
