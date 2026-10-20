"""Bounded complete-buffer POP multiline response decoder, not a POP client."""

def decode_multiline(wire,*,max_wire_bytes,max_message_bytes):
    if not isinstance(wire,bytes) or any(type(n) is not int or n<0 for n in [max_wire_bytes,max_message_bytes]):
        raise ValueError('invalid input or limits')
    if len(wire)>max_wire_bytes:raise ValueError('wire limit')
    end=wire.find(b'\r\n')
    if end<0:raise ValueError('incomplete status')
    status=wire[:end]
    if end+2>512 or b'\n' in status or b'\r' in status:raise ValueError('invalid status')
    if status==b'-ERR' or status.startswith(b'-ERR '):
        return {'state':'negative','remaining':wire[end+2:]}
    if status!=b'+OK' and not status.startswith(b'+OK '):raise ValueError('invalid status')
    cursor=end+2;parts=[];size=0
    while True:
        end=wire.find(b'\r\n',cursor)
        if end<0:raise ValueError('incomplete multiline response')
        line=wire[cursor:end];cursor=end+2
        if b'\n' in line or b'\r' in line:raise ValueError('invalid line ending')
        if line==b'.':return {'state':'complete','message':b''.join(parts),'remaining':wire[cursor:]}
        if line.startswith(b'.'):line=line[1:]
        size+=len(line)+2
        if size>max_message_bytes:raise ValueError('message limit')
        parts.append(line+b'\r\n')
