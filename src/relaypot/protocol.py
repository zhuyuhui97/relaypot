from twisted.internet.protocol import Protocol
from twisted.python import log, failure, components
from twisted.logger import Logger
from twisted.internet import reactor
from twisted.application.internet import TCPClient

import relaypot.factory
from relaypot.util import create_endpoint_services

from relaypot.top_service import top_service


class MyProtocol(Protocol):

    log = Logger()

    def connectionMade(self):
        self.host_addr = self.transprt.getHost()
        self.peer_addr = self.transport.getPeer()
        self.log.info("Got conn {addr} -> :{port}",
                      addr=self.peer_addr.host, port=self.host_addr.port)
        self.setup_upstream()
        # set session info here
        #self.make_upstream_conn()

    def connectionLost(self, reason: failure.Failure):
        self.log.info("Lost conn {addr} -> :{port}",
                      addr=self.peer_addr.host, port=self.host_addr.port)
        self.close_upstream()

    def dataReceived(self, data: bytes):
        self.log.info("Got data {addr} -> :{port} = {data!r}",
                      addr=self.peer_addr.host, port=self.host_addr.port, data=data)
        # reactor
        self.start_service()

    def setup_upstream(self):
        self.upstream = TCPClient()
        
    def set_upstream(self, downstream):
        self.downstream = downstream()

    def close_upstream(self):
        pass

    def send_upstream(self, buf):
        pass

    def recv_upstream(self, buf):
        self.transport.write(buf)

    def start_service(self):
        factory = relaypot.factory.MyFactory()
        listen_endpoints = "tcp:2325:interface=0.0.0.0".split()
        create_endpoint_services(reactor, top_service, listen_endpoints, factory)
        pass

    def close_service(self):
        pass
