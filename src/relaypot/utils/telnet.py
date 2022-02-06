import hashlib
import re
import bashlex
from twisted.logger import Logger

class TelnetHandler:
    _log_basename = 'TelnetHandler'
    REQ_USERNAME = b'login:'
    REQ_PASSWORD = b'Password:'
    STATUS_NO_AUTH = 0
    STATUS_REQ_USERNAME = 1
    STATUS_REQ_PASSWORD = 2
    STATUS_AUTH_DONE = 3

    @staticmethod
    def pre_init():
        TelnetHandler.dl_cmds = []
        with open('etc/dl_cmds.txt', 'r') as dl_cmds_f:
            items = dl_cmds_f.readlines()
            for item in items:
                TelnetHandler.dl_cmds.append(item.strip())

    def __init__(self, fproto) -> None:
        self.STATUS = self.STATUS_NO_AUTH
        self._req_frag = None
        self._resp_frag = None
        self._linebuf = b''
        self.fproto = fproto

    def on_request(self, buf: bytes):
        self.truncate_response(buf)
        # TODO Process \xff
        if self.STATUS == self.STATUS_REQ_USERNAME:
            if buf.endswith(b'\r\n') or buf.endswith(b'\x00'):
                new_buf = self.cred[0].encode() + b'\r\n'
            else:
                return None
        elif self.STATUS == self.STATUS_REQ_PASSWORD:
            if buf.endswith(b'\r\n') or buf.endswith(b'\x00'):
                new_buf = self.cred[1].encode() + b'\r\n'
            else:
                return None
        else:
            new_buf = buf
        if self.STATUS == self.STATUS_AUTH_DONE:
            lines = self.commit_lines(buf)
            for line in lines:
                try:
                    parsed = self.parse_line(line.decode())
                    for parsed_item in parsed:
                        self.get_download(parsed_item)
                except:
                    pass
        return new_buf

    def on_response(self, buf: bytes):
        self.truncate_request(buf)
        self.set_status(buf)

    def on_close(self):
        self.truncate_request(None)
        self.truncate_response(None)
        self.fproto = None

    def set_status(self, buf: bytes):
        if self.STATUS == self.STATUS_NO_AUTH and self.REQ_USERNAME in buf:
            self.STATUS = self.STATUS_REQ_USERNAME
        elif self.STATUS == self.STATUS_REQ_USERNAME and self.REQ_PASSWORD in buf:
            self.STATUS = self.STATUS_REQ_PASSWORD
        elif self.STATUS == self.STATUS_REQ_PASSWORD:
            self.STATUS = self.STATUS_AUTH_DONE

    def commit_lines(self, new_req_buf: bytes):
        _lines = re.split(b'\n|\r\n|\x00', new_req_buf)
        _lines[0] = self._linebuf + _lines[0]
        self._linebuf = _lines[-1]
        return _lines[:-1]

    def truncate_request(self, new_resp_buf: bytes or None):
        if self._req_frag != None:
            args = {
                'buf': repr(self._req_frag),
                'hash': hashlib.md5(self._req_frag).hexdigest()
            }
            self.fproto.sess_log.on_event(event='req_part', args=args)
            self._req_frag = None
        if self._resp_frag == None:
            self._resp_frag = new_resp_buf
        elif new_resp_buf != None:
            self._resp_frag = self._resp_frag + new_resp_buf

    def truncate_response(self, new_req_buf: bytes or None):
        if self._resp_frag != None:
            args = {
                'buf': repr(self._resp_frag),
                'hash': hashlib.md5(self._resp_frag).hexdigest()
            }
            self.fproto.sess_log.on_event(event='resp_part', args=args)
            self._resp_frag = None
        if self._req_frag == None:
            self._req_frag = new_req_buf
        elif new_req_buf != None:
            self._req_frag = self._req_frag + new_req_buf

    def parse_endpoint_str(self, endpoint: str):
        _epstr = endpoint.split('@')
        self.cred = _epstr[0].split(':')
        self.point = _epstr[1].split(':')
        self._log = Logger(namespace=self._log_basename + ' ' + endpoint)
        return self.point[0], int(self.point[1])

    def parse_line(self, line: str):
        try:
            return bashlex.parse(line.strip())
        except Exception:
            self._log.error('Failed to parse line ' + line)
            return None

    def get_download(self, cmd):
        from queue import Queue
        q = Queue()
        q.put(cmd)
        while not q.empty():
            current = q.get()
            if current.kind == 'command':
                parts = current.parts
                if parts[0].kind == 'word':
                    if 'busybox' in parts[0].word:
                        parts = parts[1:]
                    if parts[0].word in TelnetHandler.dl_cmds and len(parts) > 1:
                        print(parts)
                        # TODO Log download
                        line = self.reassemble_cmd(current)
                        self.fproto.sess_log.on_download(line)
            if hasattr(current, 'parts'):
                for item in current.parts:
                    q.put(item)

    def reassemble_cmd(self, cmd):
        line = ''
        if cmd.kind != 'command':
            return None
        for item in cmd.parts:
            if item.kind == 'word':
                line += item.word + ' '
        return line