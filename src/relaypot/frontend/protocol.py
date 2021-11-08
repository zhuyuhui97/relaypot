from twisted.internet.protocol import Protocol
from twisted.python import failure
from twisted.logger import Logger
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint

from relaypot.frontend.util import create_endpoint_services
from relaypot.frontend.backend import BackendClientFactory
from relaypot.frontend.top_service import top_service
from relaypot import utils


class FrontendProtocol(Protocol):

    twlog = Logger()

    def connectionMade(self):
        self.backend_host = utils.global_config['backend']['host']
        self.backend_port = utils.global_config['backend']['port']
        self.bproto = None
        self.buf_to_send = []
        self.host_addr = self.transport.getHost()
        self.peer_addr = self.transport.getPeer()
        self.twlog.info("Got peer connection {addr} -> :{port}",
                        addr=self.peer_addr.host, port=self.host_addr.port)
        self.setup_backend()
        # set session info here
        # self.make_upstream_conn()

    def connectionLost(self, reason: failure.Failure):
        self.twlog.info("Lost peer connection {addr} -> :{port}",
                        addr=self.peer_addr.host, port=self.host_addr.port)
        self.close_backend()

    def dataReceived(self, data: bytes):
        self.to_backend(data)

    def setup_backend(self):
        f = BackendClientFactory(self)
        point = TCP4ClientEndpoint(
            reactor, self.backend_host, self.backend_port, timeout=20)
        d = point.connect(f)
        d.addCallback(self.on_bproto_connected)
        d.addErrback(self.on_bproto_error)

    def on_bproto_connected(self, bproto):
        self.twlog.info('Got bproto {}.'.format(str(bproto)))
        self.set_bproto(bproto)

    def on_bproto_error(self, reason):
        self.twlog.info('Failed to connect to backend, closing connection to client: {reason}', reason=reason)
        self.transport.loseConnection()

    def set_bproto(self, bproto):
        self.bproto = bproto

    def close_backend(self):
        if self.bproto != None:
            self.twlog.info('Closing connection to backend.')
            self.bproto.transport.loseConnection()

    def to_backend(self, buf):
        if self.bproto == None:
            self.twlog.info('Buffering bytes when bproto is not ready.')
            self.buf_to_send.append(buf)
        else:
            self.bproto.send_backend(buf)
