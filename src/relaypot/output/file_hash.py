import json
import os

import pandas as pd
import redis

from relaypot.output import null
from relaypot import utils


class Writer(null.Writer):
    REDIS_DB_REQ = 14
    REDIS_DB_RSP = 15
    @staticmethod
    def pre_init():
        if utils.global_config == None:
            # TODO raise another exception
            raise Exception
        Writer.config = utils.global_config['backend']['file_hash']
        Writer.redis_req = redis.Redis(**Writer.config['redis'], decode_responses=True, db=Writer.REDIS_DB_REQ)  
        Writer.redis_rsp = redis.Redis(**Writer.config['redis'], decode_responses=True, db=Writer.REDIS_DB_RSP)  
        Writer.basedir = Writer.config['file']['base']

    def __init__(self, sid: str, sess) -> None:
        super().__init__(sid, sess)
        self.filepath = os.path.join(Writer.basedir, sid+'.json')
        self.logs = []
        self.last_event = {'hash': 'START', 'req': None}
        self.req_frag = 0
        self.rsp_frag = 0
        self.req_update = 0
        self.rsp_update = 0

    def write(self, logentry):
        if logentry['eventid'] == self.EV_CLI_SYN:
            self.start_time = logentry['timestamp']
        elif logentry['eventid'] in [self.EV_CLI_FIN, self.EV_SRV_RST]:
            self.last_event['next_hash'] = 'FIN'
            self.last_event['next_req'] = None
        elif logentry['eventid'] in [self.EV_CLI_REQ, self.EV_SRV_RSP]:
            if logentry['eventid'] == self.EV_CLI_REQ:
                self.req_update += Writer.redis_req.setnx(logentry['hash'], repr(logentry['buf']))
                self.req_frag += 1
            elif logentry['eventid'] == self.EV_SRV_RSP:
                self.rsp_update += Writer.redis_rsp.setnx(logentry['hash'], repr(logentry['buf']))
                self.rsp_frag += 1
            is_req = True if logentry['eventid'] == self.EV_CLI_REQ else False
            _logentry = {
                'prev_hash': self.last_event['hash'],
                'prev_req': self.last_event['req'],
                'hash': logentry['hash'],
                'req': is_req,
                'time': (logentry['timestamp']-self.start_time).total_seconds()
            }
            self.last_event['next_hash'] = logentry['hash']
            self.last_event['next_req'] = is_req
            self.last_event = _logentry
            self.logs.append(_logentry)

    def close(self):
        # 'sid': self.sess.sid,
        # 'timestamp': str(self.start_time),
        # 'src_ip': self.sess.src_ip,
        # 'src_port': self.sess.src_port,
        # 'dst_ip': self.sess.dest_ip,
        # 'dst_port': self.sess.dest_port,
        # 'back_rev': self.sess.git_rev,
        # 'req_frag': self.req_frag,
        # 'req_update': self.req_update,
        # 'rsp_frag': self.rsp_frag,
        # 'rsp_update': self.rsp_update,
        # 'agent_info': self.sess.agent_info,
        # 'log': self.logs
        summary_obj = {
            **self.sess.base_info,
            'timestamp': str(self.start_time),
            'req_frag': self.req_frag,
            'req_update': self.req_update,
            'rsp_frag': self.rsp_frag,
            'rsp_update': self.rsp_update,
            'log': self.logs,
        }
        with open(self.filepath, 'a') as of:
            json.dump(summary_obj, of)
