"""One-message loopback SMTP fixture. No relay, authentication or TLS service."""
import queue
import smtplib
import socket
import threading
MAX_WIRE=2097152

def roundtrip(wire):
    if not isinstance(wire,bytes) or len(wire)>MAX_WIRE or not wire.endswith(b'\r\n'):
        raise ValueError('Bounded CRLF message required')
    if b'\n' in wire.replace(b'\r\n',b''):raise ValueError('Noncanonical line endings')
    listener=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    listener.bind(('127.0.0.1',0));listener.listen(1);listener.settimeout(5)
    port=listener.getsockname()[1];result=queue.Queue()
    def receive():
        try:
            with listener:
                connection,_=listener.accept()
                with connection:
                    connection.settimeout(5)
                    with connection.makefile('rwb') as stream:
                        def reply(value):stream.write(value);stream.flush()
                        def line():
                            value=stream.readline(1002)
                            if not value or not value.endswith(b'\r\n') or len(value)>1001:raise ValueError('Invalid fixture SMTP line')
                            return value
                        reply(b'220 localhost fixture\r\n')
                        sender=False;recipient=False;delivered=False
                        while True:
                            command=line().upper()
                            if command.startswith(b'EHLO ') or command.startswith(b'HELO '):
                                reply(b'250 localhost\r\n')
                            elif command.startswith(b'MAIL FROM:') and not delivered:
                                sender=True;recipient=False;reply(b'250 sender accepted\r\n')
                            elif command.startswith(b'RCPT TO:') and sender and not delivered:
                                recipient=True;reply(b'250 recipient accepted\r\n')
                            elif command==b'DATA\r\n' and recipient and not delivered:
                                reply(b'354 send message\r\n');parts=[];size=0
                                while True:
                                    value=line()
                                    if value==b'.\r\n':break
                                    if value.startswith(b'..'):value=value[1:]
                                    size+=len(value)
                                    if size>MAX_WIRE:raise ValueError('Fixture message bound')
                                    parts.append(value)
                                result.put(b''.join(parts));delivered=True;reply(b'250 accepted\r\n')
                            elif command==b'QUIT\r\n':
                                reply(b'221 closing\r\n');return
                            else:reply(b'503 unsupported fixture sequence\r\n')
        except BaseException as error:result.put(error)
    worker=threading.Thread(target=receive,daemon=True);worker.start()
    try:
        with smtplib.SMTP('127.0.0.1',port,timeout=5) as client:
            refused=client.sendmail('alice@example.invalid',['bob@example.invalid'],wire)
            if refused:raise ValueError('Fixture recipient refused')
    finally:
        listener.close();worker.join(timeout=6)
    if worker.is_alive():raise TimeoutError('Fixture receiver did not stop')
    received=result.get_nowait()
    if isinstance(received,BaseException):raise received
    return received
