import hashlib
import re
from telnetlib import Telnet
import bashlex
from twisted.logger import Logger
import pickle
from sklearn.feature_extraction.text import CountVectorizer, HashingVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
        # Do modification on request buffer
        # TODO Process \xff
        if self.STATUS == self.STATUS_REQ_USERNAME:
            new_buf = self.preproc_username(buf)
        elif self.STATUS == self.STATUS_REQ_PASSWORD:
            new_buf = self.preproc_password(buf)
        elif self.STATUS == self.STATUS_AUTH_DONE:
            new_buf = buf
            self.pending_lines = self.commit_lines(buf)
        else:
            new_buf = buf
        # Submit request to downstream processor
        self.submit_req(new_buf)
        # Extract other information
        if self.STATUS == self.STATUS_AUTH_DONE:
            self.postproc_cmdline(buf)
        # return new_buf

    def preproc_username(self, buf):
        if buf.endswith(b'\r\n') or buf.endswith(b'\x00'):
            return self.cred[0].encode() + b'\r\n'
        else:
            return None

    def preproc_password(self, buf):
        if buf.endswith(b'\r\n') or buf.endswith(b'\x00'):
            return self.cred[1].encode() + b'\r\n'
        else:
            return None

    def handle_cmdline(self, buf):
        pass
    
    def submit_req(self, buf):
        self.pending_req = buf

    def postproc_cmdline(self, buf):
        for line in self.pending_lines:
            try:
                parsed = self.parse_line(line.decode())
                for parsed_item in parsed:
                    self.get_download(parsed_item)
            except:
                pass

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

class TelnetHandlerLIH(TelnetHandler):
    @staticmethod
    def pre_init():
        TelnetHandlerLIH.tokenizer = None
        TelnetHandlerLIH.hc = None
        TelnetHandlerLIH.resp_parts_buf = None
        with open('etc/profiles/req_hc.pkl') as pkl:
            TelnetHandlerLIH.hc = pickle.load(pkl)
        with open('etc/profiles/req_tokenizer.pkl') as pkl:
            TelnetHandlerLIH.tokenizer = pickle.load(pkl)
        with open('etc/profiles/resp_parts_buf.pkl') as pkl:
            TelnetHandlerLIH.resp_parts_buf = pickle.load(pkl)
        pickle.load()
    
    def submit_req(self, buf):
        if self.STATUS == self.STATUS_REQ_USERNAME:
            pass
        elif self.STATUS == self.STATUS_REQ_PASSWORD:
            pass
        elif self.STATUS == self.STATUS_AUTH_DONE:
            lines = self.pending_lines
            self.handle_cmdline(buf)
            # TODO prepare response here
        else:
            pass
        

    def _tokenizer(self, string: bytes):
        BYTE_OTHER = 0
        BYTE_PUNC = 1
        BYTE_CHAR = 2
        # if isinsta`nce(string, str):
        #     string = bytes(string, encoding='latin-1')
        strlen = len(string)
        tokens = []
        _old_type = None
        for ptr in range(0, strlen):
            _current = ord(string[ptr])
            _current_type = BYTE_PUNC
            if (
                (_current >= 0x30 and _current <= 0x39)
                or (_current >= 0x41 and _current <= 0x5A)
                or (_current >= 0x61 and _current <= 0x7A)
            ):
                _current_type = BYTE_CHAR
            elif _current <= 0x1F and _current >= 0x7F:
                _current_type = BYTE_OTHER
            if _current_type == _old_type:
                tokens[-1] += string[ptr]
            else:
                tokens.append(string[ptr])
            _old_type = _current_type
        return tokens

    def resp_by_pred(self, pred):
        return 

    def handle_cmdline(self, buf):
        tokens = TelnetHandlerLIH.tokenizer.transform([buf])
        pred = TelnetHandlerLIH.hc.fit_predict(tokens)


        bufs = []# TODO 参照ipynb中的向量化过程，使用去掉变动关键词的词典，测算距离。
        
    def on_response(self, buf):
        pass
    
