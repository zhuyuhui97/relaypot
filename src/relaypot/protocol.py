from twisted.internet.protocol import Protocol
from twisted.python import log, failure, components
from twisted.logger import Logger
from twisted.internet import reactor

import relaypot.factory
from relaypot.util import create_endpoint_services

from relaypot.top_service import top_service


class MyProtocol(Protocol):

    log = Logger()

    def connectionMade(self):
        self.host_addr = self.transport.getHost()
        self.peer_addr = self.transport.getPeer()
        self.log.info("Got conn {addr} -> :{port}",
                      addr=self.peer_addr.host, port=self.host_addr.port)

    def connectionLost(self, reason: failure.Failure):
        self.log.info("Lost conn {addr} -> :{port}",
                      addr=self.peer_addr.host, port=self.host_addr.port)

    def dataReceived(self, data: bytes):
        self.log.info("Got data {addr} -> :{port} = {data!r}",
                      addr=self.peer_addr.host, port=self.host_addr.port, data=data)
        # reactor
        self.start_service()

    def start_service(self):
        factory = relaypot.factory.MyFactory()
        listen_endpoints = "tcp:2325:interface=0.0.0.0".split()
        create_endpoint_services(reactor, top_service, listen_endpoints, factory)
        pass

    def close_service(self):
        pass
