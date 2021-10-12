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


class BackendServerProtocol(LineOnlyReceiver):

    log = Logger()
    db_logger = LogEncoder

    def connectionMade(self):
        self.buf_to_proc = []
        self.session_info = None
        self.sess_log = None
        pass
        # set session info here
        #self.make_upstream_conn()

    def lineReceived(self, line):
        if self.session_info == None:
            self.decode_preamble(line)
        else:
            self.decode_buf(line)
        

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


    def decode_buf(self, buf):
        obj = json.loads(buf)
        msg_buf = eval(obj['buf'])
        self.sess_log.on_request(msg_buf)




