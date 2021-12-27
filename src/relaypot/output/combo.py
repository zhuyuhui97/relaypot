from relaypot.output.elastic import Writer as esw
from relaypot.output.file_hash import Writer as fhw
from relaypot.output import null


class Writer(null.Writer):
    @staticmethod
    def pre_init():
        fhw.pre_init()
        esw.pre_init()

    def __init__(self, sid: str, sess) -> None:
        self.fhw = fhw(sid, sess)
        self.esw = esw(sid, sess)

    def write(self, logentry):
        if logentry['eventid'] in [self.EV_SRV_RSP, 'req_part']:
            return
        self.fhw.write(logentry=logentry)
        self.esw.write(logentry=logentry)

    def close(self):
        self.fhw.close()
        self.esw.close()
