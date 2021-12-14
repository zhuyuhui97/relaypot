from typing import Tuple
import json
from queue import Queue

from twisted.python import failure
from twisted.internet.protocol import ClientFactory, Protocol
from twisted.logger import Logger


class BackendClientProtocol(Protocol):

    _log_basename = 'BCliProto'

    def __init__(self) -> None:
        self._log = Logger()
        self.fproto = None
        self.buf_to_send = Queue()
        super().__init__()

    def connectionMade(self):
        self.back_addr = self.transport.getPeer()

    def connectionLost(self, reason: failure.Failure):
        self._log.info('Lost backend connection {bhost}:{port}. reason:{reason}',
                       bhost=self.back_addr.host,
                       port=self.back_addr.port,
                       reason=reason)
        super().connectionLost(reason=reason)
        self.fproto.transport.loseConnection()
        self.fproto = None
        # TODO Protocol call <pair>.transport.loseConnection() in self.connectionLost() may make self.connectionLost() called again.

    def dataReceived(self, data: bytes):
        if self.fproto == None:
            self.buf_to_send.put(data)
        else:
            self.sendto_frontend(data)

    def sendto_frontend(self, data):
        self.fproto._log.info('p <- f -- {buf}', buf=data)
        self.fproto.transport.write(data)

    def sendto_backend(self, buf):
        self.fproto._log.info('p -> f -- {buf}', buf=buf)
        self.transport.write(self.encode_buf(buf))

    def set_fproto(self, fproto):
        self.fproto = fproto
        self.peer_addr = fproto.peer_addr
        self.host_addr = fproto.host_addr
        self.setup_log_namespace()
        self._log.info('Made backend connection {bhost}:{port}.',
                       bhost=self.back_addr.host, port=self.back_addr.port)
        self.transport.write(self.encode_info())  # TODO Rename
        # BUG May not drain properly
        self.drain_f2b_queue()
        self.drain_b2f_queue()

    def drain_f2b_queue(self):
        while not self.fproto.buf_to_send.empty():
            self.sendto_backend(self.fproto.buf_to_send.get())

    def drain_b2f_queue(self):
        while not self.buf_to_send.empty():
            self.sendto_frontend(self.buf_to_send.get())

    def encode_info(self):
        obj = {
            'dest_ip': self.host_addr.host,
            'dest_port': self.host_addr.port,
            'src_ip': self.peer_addr.host,
            'src_port': self.peer_addr.port,
        }
        return json.dumps(obj).encode() + b'\r\n'

    def encode_buf(self, buf):
        escaped_buf = repr(buf)
        obj = {
            'length': len(buf),
            'hashsum': '',
            'buf': escaped_buf
        }
        return json.dumps(obj, ensure_ascii=False).encode()+b'\r\n'
        # TODO

    def setup_log_namespace(self):
        self._log.namespace = "{basename:<10} p{peer_addr}->f:{fproto_port}->b{bproto_addr}:{bproto_port}".format(
            basename=self._log_basename,
            peer_addr=self.peer_addr.host,
            fproto_port=str(self.host_addr.port),
            bproto_addr=self.back_addr.host,
            bproto_port=self.back_addr.port)
