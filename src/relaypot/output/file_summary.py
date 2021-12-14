import json
import os

from relaypot.output import null
from relaypot import utils


class Writer(null.Writer):

    @staticmethod
    def pre_init():
        if utils.global_config == None:
            # TODO raise another exception
            raise Exception
        Writer.config = utils.global_config['backend']['filelog']
        Writer.basedir = Writer.config['base']

    def __init__(self, sid: str, sess) -> None:
        super().__init__(sid, sess)
        self.filepath = os.path.join(Writer.basedir, sid+'.json')
        self.ofile = open(self.filepath, 'a')
        self.logs = []

    def write(self, logentry):
        logentry['timestamp'] = str(logentry['timestamp'])
        self.ofile.write(json.dumps(logentry))
        self.ofile.write('\n')
        self.logs.append(logentry)

    def close(self):
        self.ofile.close()
        summ_path = os.path.join(Writer.basedir, 'summary.json')
        total_len = len(self.logs)-2
        stat = Writer.map_resp(Writer.session_hash(self.logs))
        has_download = False
        idx = 0
        while has_download == False and idx < total_len:
            if 'buf' in self.logs[idx]: has_download |= Writer.part_has_download(self.logs[idx])
            idx = idx + 1
        with open(summ_path, 'a') as of:
            s = json.dumps({
                'start_time': self.logs[0]['timestamp'],
                'end_time': self.logs[-1]['timestamp'],
                'addr': self.logs[0]['src_ip'],
                'sess_id': self.logs[0]['sid'],
                'len':total_len,
                'dl': has_download,
                'stat': stat
            })
            of.write(s)
            of.write('\n')
    
    @staticmethod
    def session_hash(sesslog):
        sess_frags = []
        sess_len = len(sesslog)
        part = None
        for idx in range(sess_len):
            frag = sesslog[idx]
            if 'response' in frag['eventid'] or 'request' in frag['eventid']:
                is_req = True if 'request' in frag['eventid'] else False
                # md5sum = hashlib.md5(eval(frag['buf'])).hexdigest()
                part = {
                    'buf': frag['buf'],
                    'req': is_req,
                    'hash': ''
                }
                sess_frags.append(part)
            elif 'disconnect' in frag['eventid']:
                part = {
                    'req': None,
                }
                sess_frags.append(part)
        return sess_frags

    @staticmethod
    def part_has_download(part):
        for keyword in ['wget', 'curl', 'tftp', 'chmod']:
            if keyword in part['buf'] and 'http' in part['buf']:
                return True
        return False

    @staticmethod
    def map_resp(sess_frags):
        sess_len = len(sess_frags)
        idx = 0
        cnt_req_frag = 0
        cnt_req_part = 0
        cnt_resp_frag = 0
        cnt_resp_part = 0
        while idx < sess_len:
            frag = sess_frags[idx]
            if frag['req'] == None:
                break
            if frag['req'] == False and idx == 0:
                pass
            elif frag['req'] == True:
                req_frags, offset = Writer.get_frag_range(sess_frags[idx:], is_req=True)
                idx = idx + offset
                cnt_req_frag = cnt_req_frag + offset
                cnt_req_part = cnt_req_part + 1
                if idx+1 == sess_len or sess_frags[idx]['req'] == None:
                    break
            resp_frags, offset = Writer.get_frag_range(sess_frags[idx:], is_req=False)
            idx = idx+offset
            cnt_resp_frag = cnt_resp_frag + offset
            cnt_resp_part = cnt_resp_part + 1
        return {
            'cnt_req_frag': cnt_req_frag,
            'cnt_req_part': cnt_req_part,
            'cnt_resp_frag': cnt_resp_frag,
            'cnt_resp_part': cnt_resp_part
        }
            
    @staticmethod
    def get_frag_range(sess_frags, is_req):
        offset = 0
        parts_len = len(sess_frags)
        while is_req == sess_frags[offset]['req']:
            offset = offset+1
            if offset>parts_len-1 or sess_frags[offset]['req'] == None:
                break
        return sess_frags[0:offset], offset
