import datetime, hashlib

from relaypot import utils


class BaseOutput():
    def __init__(self, sid: str, src_ip: str, src_port: int, dest_ip: str, dest_port: int, agent_info=None) -> None:
        self.src_ip = src_ip
        self.src_port = src_port
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.sid = sid
        self.git_rev = utils.git_rev
        self.agent_info = agent_info
        self.set_base_info()
        # HACK CROSS REFERENCE MAY CAUSE MEMORY LEAK
        self.writer = utils.cls_writer(sid, self)
        self.on_connected()

    def get_timestamp(self):
        return datetime.datetime.utcnow()
        
    def on_connected(self):
        obj = self.fill_base_info()
        obj['eventid'] = self.writer.EV_CLI_SYN
        self.writer.write(obj)

    def on_disconnected(self):
        obj = self.fill_base_info()
        obj['eventid'] = self.writer.EV_CLI_FIN
        self.writer.write(obj)
        self.writer.close()
        # HACK Dereference manually to avoid memory leak
        self.writer = None

    def on_request(self, buf: bytes):
        obj = self.fill_base_info()
        obj['eventid'] = self.writer.EV_CLI_REQ
        obj['buf'] = repr(buf)
        obj['hash'] = hashlib.md5(buf).hexdigest()
        self.writer.write(obj)

    def on_response(self, buf: bytes):
        obj = self.fill_base_info()
        obj['eventid'] = self.writer.EV_SRV_RSP
        obj['buf'] = repr(buf)
        obj['hash'] = hashlib.md5(buf).hexdigest()
        self.writer.write(obj)
    
    def on_download(self, cmd: str):
        obj = self.fill_base_info()
        obj['eventid'] = self.writer.EV_CLI_DL
        obj['cmd'] = cmd
        self.writer.write(obj)

    def set_base_info(self) -> dict:
        self.base_info = {
            'sid': self.sid,
            'src_ip': self.src_ip,
            'src_port': self.src_port,
            'dst_ip': self.dest_ip,
            'dst_port': self.dest_port,
            'back_rev': self.git_rev,
            'agent_info': self.agent_info
        }

    def fill_base_info(self) -> dict:
        obj = {
            **self.base_info,
            'timestamp': self.get_timestamp()
        }
        return obj
