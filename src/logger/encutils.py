from logger.baselogger import BaseLogger
from logger.elastic import EsOutput


class LogEncoder(BaseLogger):
    def __init__(self, src_ip: str, src_port: int, dest_ip: str, dest_port: int, logger: BaseLogger = EsOutput) -> None:
        self.logger = logger()
        self.src_ip = src_ip
        self.src_port = src_port
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.on_connected()

    def on_connected(self):
        obj = self.fill_base_info()
        obj['eventid'] = 'relaypot.session.connected',
        self.logger.write(obj)

    def on_disconnected(self):
        obj = self.fill_base_info()
        obj['eventid'] = 'relaypot.session.disconnected',
        self.logger.write(obj)

    def on_request(self, buf: bytes):
        obj = self.fill_base_info()
        obj['eventid'] = 'relaypot.session.request',
        obj['buf'] = repr(buf)
        self.logger.write(obj)

    def on_response(self, buf: bytes):
        obj = self.fill_base_info()
        obj['eventid'] = 'relaypot.session.response',
        obj['buf'] = repr(buf)
        self.logger.write(obj)

    def fill_base_info(self) -> dict:
        obj = {
            'src_ip': self.src_ip,
            'src_port': self.src_port,
            'dst_ip': self.dest_ip,
            'dst_port': self.dest_port,
            'timestamp': self.get_timestamp()
        }
        return obj
