import json
import traceback

from twisted.protocols.basic import LineOnlyReceiver
from twisted.python import failure
from twisted.logger import Logger

from relaypot.frontend.util import create_endpoint_services
from relaypot.backend.top_service import top_service
from relaypot.output import BaseOutput
from relaypot.utils.vars import gen_sessid
from relaypot import utils


class BackendServerProtocol(LineOnlyReceiver):
    # TODO Sometimes log service may unavailable. Trying to connect to the service will throw an exception, which may interrupt the backend service and stop it from cleaning frontent connection.

    _log_basename = 'BSrvProto'
    db_logger = BaseOutput

    def __init__(self) -> None:
        super().__init__()
        self._log = Logger(namespace=self._log_basename)

    def connectionMade(self):
        self.front_addr = self.transport.getPeer()
        self.resp_to_log = []
        self.session_info = None
        self.sess_log = None
        self.agent = None
        self.sid = gen_sessid()
        self._log.info(
            "Got frontend connection {id}: {host}:{port}", id=self.sid, host=self.front_addr.host, port=self.front_addr.port)

    def lineReceived(self, line):
        if self.session_info == None:
            self.decode_preamble(line)
            if len(self.resp_to_log) > 0:
                self._log.info(
                    'Commiting {count} buffered logs.', count=len(self.resp_to_log))
                for buf in self.resp_to_log:
                    self.sess_log.on_response(buf)
                self.resp_to_log.clear()
        else:
            req = self.decode_buf(line)
            if req == None:
                return
            self._log.info('p -> f -- {buf}', buf=req)
            self.agent.on_request(req)

    def connectionLost(self, reason: failure.Failure):
        if self.agent != None:
            self.agent.on_front_lost(reason)
        if self.sess_log != None:
            self.sess_log.on_disconnected()
        self._log.info("Lost frontend connection. reason:{reason}", reason=reason)

    def decode_preamble(self, buf):
        self._log.info('Got preamble: buf={buf}', buf=buf)
        try:
            self.session_info = json.loads(buf)
            self.setup_log_namespace()
            self.init_agent()
            self.sess_log = self.db_logger(sid=self.sid, **self.session_info)
        except Exception as e:
            self._log.error(
                'Failed to parse preamble: buf={buf}, e={e}', buf=buf, e=e)
            self._log.error(traceback.format_exc())
            self.transport.loseConnection()

    def setup_log_namespace(self):
        self._log.namespace = '{basename:<10} {sid} p{src_ip}->f{dest_ip}:{dest_port}'.format(
                sid=self.sid,
                basename=self._log_basename, 
                **self.session_info)

    def decode_buf(self, buf):
        try:
            obj = json.loads(buf)
            msg_buf = eval(obj['buf'])
            self.sess_log.on_request(msg_buf)
            return msg_buf
        except Exception as e:
            self._log.error(
                'Failed to parse request: buf={buf}, e={e}', buf=buf, e=e)
            self._log.error(traceback.format_exc())
            return None

    def init_agent(self):
        self.agent = utils.cls_agent(self)
        self.agent.on_init()

    def send_response(self, buf_seq):
        if buf_seq == None:
            return
        for buf in buf_seq:
            if isinstance(buf, str):
                buf = buf.encode()
            if self.sess_log == None:
                self._log.warn(
                    'Buffering logs when log service is not ready.')
                self.resp_to_log.append(buf)
            else:
                self.sess_log.on_response(buf)
            self._log.info('p <- f -- {buf}', buf=buf)
            self.transport.write(buf)
