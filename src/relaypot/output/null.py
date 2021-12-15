class Writer():
    EV_CLI_SYN = 'connected'
    EV_CLI_FIN = 'disconnected'
    EV_SRV_RST = 'server_rst'
    EV_CLI_REQ = 'request'
    EV_SRV_RSP = 'response'
    EV_SRV_DL = 'download'

    @staticmethod
    def pre_init():
        return

    def __init__(self, sid: str, sess) -> None:
        self.sid = sid
        self.sess = sess

    def write(self, logentry):
        return

    def close(self):
        return
