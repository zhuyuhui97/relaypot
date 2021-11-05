from twisted.internet.protocol import Protocol
from twisted.python import log, failure, components
from twisted.logger import Logger
from twisted.internet import reactor
from twisted.application.internet import TCPClient
from twisted.internet.endpoints import TCP4ClientEndpoint

import relaypot.factory
from relaypot.util import create_endpoint_services
from relaypot.backend import BackendClientFactory
from relaypot.top_service import top_service
import utils

class FrontendProtocol(Protocol):

    log = Logger()

    def connectionMade(self):
        self.backend_host = utils.global_config['backend']['client']['server']['host']
        self.backend_port = utils.global_config['backend']['client']['server']['port']
        self.backend_prot = None
        self.buf_to_send = []
        self.host_addr = self.transport.getHost()
        self.peer_addr = self.transport.getPeer()
        self.log.info("Got conn {addr} -> :{port}",
                      addr=self.peer_addr.host, port=self.host_addr.port)
        self.setup_backend()
        # set session info here
        #self.make_upstream_conn()

    def connectionLost(self, reason: failure.Failure):
        self.log.info("Lost conn {addr} -> :{port}",
                      addr=self.peer_addr.host, port=self.host_addr.port)
        self.close_backend()

    def dataReceived(self, data: bytes):
        self.log.info("Got data {addr} -> :{port} = {data!r}",
                      addr=self.peer_addr.host, port=self.host_addr.port, data=data)
        self.to_backend(data)      
        # reactor

    def setup_backend(self):
        f = BackendClientFactory(self)
        f.host_addr = self.host_addr
        f.peer_addr = self.peer_addr
        point = TCP4ClientEndpoint(reactor, self.backend_host, self.backend_port, timeout=20)
        d = point.connect(f)
        d.addCallback(self.on_backend_connected)
        d.addErrback(self.on_backend_error)
        # self.upstream = reactor.connectTCP("localhost", 6667, f)
        # TODO 

    def on_backend_connected(self, backend_trans):
        self.log.info('123')
        pass

    def on_backend_error(self, reason):
        pass

    def set_backend_prot(self, b_prot):
        self.backend_prot = b_prot

    def close_backend(self):
        if self.backend_prot != None:
            self.backend_prot.transport.loseConnection()

    def to_backend(self, buf):
        if self.backend_prot == None:
            self.log.info('buffering buf')
            self.buf_to_send.append(buf)
        else:
            self.backend_prot.send_backend(buf)
