import json

from twisted.internet.protocol import Protocol
from twisted.protocols.basic import LineOnlyReceiver
from twisted.python import log, failure, components
from twisted.logger import Logger
from twisted.internet import reactor
from twisted.application.internet import TCPClient
from twisted.internet.endpoints import TCP4ClientEndpoint
import traceback

from relaypot.util import create_endpoint_services
from backend.top_service import top_service
from logger.encutils import LogEncoder


class BackendServerProtocol(LineOnlyReceiver):
    # TODO Sometimes log service may unavailable. Trying to connect to the service will throw an exception, which may interrupt the backend service and stop it from cleaning frontent connection.

    twlog = Logger()
    db_logger = LogEncoder

    def connectionMade(self):
        self.front_addr = self.transport.getPeer()
        self.resp_to_log = []
        self.session_info = None
        self.sess_log = None
        self.agent = None
        self.twlog.info(
            "Got frontend connection: {host}:{port}", host=self.front_addr.host, port=self.front_addr.port)

        # set session info here
        # self.make_upstream_conn()

    def lineReceived(self, line):
        if self.session_info == None:
            self.decode_preamble(line)
            if len(self.resp_to_log) > 0:
                self.twlog.info(
                    'Commiting {count} buffered logs.', count=len(self.resp_to_log))
                for buf in self.resp_to_log:
                    self.sess_log.on_response(buf)
                self.resp_to_log.clear()
        else:
            req = self.decode_buf(line)
            if req == None:
                return
            self.twlog.info('{peer_addr} -> :{fproto_port}  -- {buf}',
                            peer_addr=self.session_info['src_ip'], fproto_port=self.self.session_info['dest_port'], buf=req)
            self.send_response(self.agent.on_request(req))

    def connectionLost(self, reason: failure.Failure):
        if self.agent != None:
            self.agent.on_front_lost(reason)
        if self.sess_log != None:
            self.sess_log.on_disconnected()
        self.twlog.info(
            "Lost frontend connection: {host}:{port}", host=self.front_addr.host, port=self.front_addr.port)
        

    def decode_preamble(self, buf):
        self.twlog.info('Got preamble: buf={buf}', buf=buf)
        try:
            self.session_info = json.loads(buf)
            self.init_agent()
            self.sess_log = self.db_logger(**self.session_info)
        except Exception as e:
            self.twlog.error(
                'Failed to parse preamble: buf={buf}, e={e}', buf=buf, e=e)
                
            self.twlog.error(traceback.format_exc())
            self.transport.loseConnection()

    def decode_buf(self, buf):
        try:
            obj = json.loads(buf)
            msg_buf = eval(obj['buf'])
            self.sess_log.on_request(msg_buf)
            return msg_buf
        except Exception as e:
            self.twlog.error(
                'Failed to parse request: buf={buf}, e={e}', buf=buf, e=e)
            self.twlog.error(traceback.format_exc())
            return None

    def init_agent(self):
        self.agent = self.factory.agent_cls(self)
        self.send_response(self.agent.on_init())

    def send_response(self, buf_seq):
        if buf_seq == None:
            return
        for buf in buf_seq:
            if buf is str:
                buf = buf.encode()
            if self.sess_log == None:
                self.twlog.warn(
                    'Buffering logs when log service is not ready.')
                self.resp_to_log.append(buf)
            else:
                self.sess_log.on_response(buf)
            self.twlog.info('{peer_addr} <- :{fproto_port} -- {buf}',
                            peer_addr=self.session_info['src_ip'], fproto_port=self.session_info['dest_port'], buf=buf)
            self.transport.write(buf)
