import datetime

from relaypot import utils


class BaseOutput():
    def __init__(self, sid: str, src_ip: str, src_port: int, dest_ip: str, dest_port: int) -> None:
        self.logger = utils.cls_writer(sid)
        self.src_ip = src_ip
        self.src_port = src_port
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.sid = sid
        self.git_rev = utils.git_rev
        self.on_connected()

    def get_timestamp(self):
        return datetime.datetime.utcnow()
        
    def on_connected(self):
        obj = self.fill_base_info()
        obj['eventid'] = 'relaypot.session.connected'
        self.logger.write(obj)

    def on_disconnected(self):
        obj = self.fill_base_info()
        obj['eventid'] = 'relaypot.session.disconnected'
        self.logger.write(obj)

    def on_request(self, buf: bytes):
        obj = self.fill_base_info()
        obj['eventid'] = 'relaypot.session.request'
        obj['buf'] = repr(buf)
        self.logger.write(obj)

    def on_response(self, buf: bytes):
        obj = self.fill_base_info()
        obj['eventid'] = 'relaypot.session.response'
        obj['buf'] = repr(buf)
        self.logger.write(obj)

    def fill_base_info(self) -> dict:
        obj = {
            'src_ip': self.src_ip,
            'src_port': self.src_port,
            'dst_ip': self.dest_ip,
            'dst_port': self.dest_port,
            'timestamp': self.get_timestamp(),
            'sid': self.sid,
            'back_rev': self.git_rev
        }
        return obj
