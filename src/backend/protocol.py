import json

from twisted.internet.protocol import Protocol
from twisted.protocols.basic import LineOnlyReceiver
from twisted.python import log, failure, components
from twisted.logger import Logger
from twisted.internet import reactor
from twisted.application.internet import TCPClient
from twisted.internet.endpoints import TCP4ClientEndpoint

from relaypot.util import create_endpoint_services
from backend.top_service import top_service
from logger.encutils import LogEncoder

from agent.telnet import TelnetAgent


class BackendServerProtocol(LineOnlyReceiver):

    log = Logger()
    db_logger = LogEncoder
    agent_cls = TelnetAgent

    def connectionMade(self):
        self.buf_to_proc = []
        self.session_info = None
        self.sess_log = None
        self.agent = self.agent_cls()
        # set session info here
        # self.make_upstream_conn()

    def lineReceived(self, line):
        if self.session_info == None:
            self.decode_preamble(line)
        else:
            req = self.decode_buf(line)
            self.send_response(self.agent.on_request(req))

    def connectionLost(self, reason: failure.Failure):
        self.log.info("Lost conn")
        if self.sess_log != None:
            self.sess_log.on_disconnected()

    def decode_preamble(self, buf):
        try:
            self.session_info = json.loads(buf)
            # self.log.info('got conn from ' + str(buf['src_addr']))
        except:
            log.err('Failed to parse preamble')
            self.transport.loseConnection()
        self.sess_log = self.db_logger(**self.session_info)
        self.send_response(self.agent.on_init())

    def decode_buf(self, buf):
        obj = json.loads(buf)
        msg_buf = eval(obj['buf'])
        self.sess_log.on_request(msg_buf)
        return msg_buf

    def send_response(self, buf_seq):
        if buf_seq == None:
            return
        for buf in buf_seq:
            self.sess_log.on_response(buf)
            self.transport.write(buf.encode())
