import os
import random
import itertools
import subprocess

from twisted.internet import protocol
from twisted.python import failure

from relaypot.agent.base import BaseAgent


class Agent(BaseAgent):
    STATUS_REQ_USERNAME = 0
    STATUS_REQ_PASSWORD = 1
    STATUS_REQ_COMMAND = 2
    NON_PRINTABLE = itertools.chain(range(0x00, 0x20), range(0x7f, 0xa0))
    blacklist_name='blacklist.txt'
    blacklist_base='blacklist'

    def __init__(self, fproto:protocol.Protocol, profile_name=None, profile_base='profiles'):
        plist = os.listdir(profile_base)
        if profile_name == None:
            rnd = random.randrange(0, len(plist))
            self.profile_name = plist[rnd]
        else:
            self.profile_name = profile_name
        self.profile_base = profile_base
        self.load_profile()
        self.load_blacklist()
        self.status = self.STATUS_REQ_USERNAME
    
    def load_blacklist(self):
        self.blacklist=[]
        filepath = os.path.join(self.blacklist_base, self.blacklist_name)
        with open(filepath) as pfile:
            while True:
                line = pfile.readline()
                if line == '':
                    break
                else:
                    self.blacklist.append(line.encode())

    def load_profile(self):
        filepath = os.path.join(self.profile_base, self.profile_name)
        with open(filepath) as pfile:
            self.banner = eval(pfile.readline())
            self.username_hint = eval(pfile.readline())
            self.password_hint = eval(pfile.readline())
            self.ps = eval(pfile.readline())
            while True:
                line = pfile.readline()
                if line == '':
                    break

    def on_init(self):
        return [self.banner, self.username_hint]

    def on_request(self, buf):
        if self.status == self.STATUS_REQ_USERNAME:
            self.status = self.STATUS_REQ_PASSWORD
            return [self.password_hint]
        elif self.status == self.STATUS_REQ_PASSWORD:
            self.status = self.STATUS_REQ_COMMAND
            return [self.ps]
        else:
            resp = self.get_resp(buf)
            resp.append('\r\n')
            resp.append(self.ps)
            return resp

    def on_front_lost(self, reason: failure.Failure):
        return None

    def on_agent_lost(self):
        return None

    def get_resp(self, buf):
        # TODO How to display commands when there are non-unicode bytes?
        responses = []
        cmds = buf.split(b';')
        for cmd in cmds:
            black = False
            for black_item in self.blacklist:
                if black_item in cmd:
                    black=True
                    break
            if black:
                responses.append(b'sh: command not found.')
                continue
            elif b'echo' in cmd:
                subp = subprocess.run(cmd,stdout=subprocess.PIPE)
                subp.check_returncode()
                responses.append(subp.stdout)
            else:
                responses.append(b'sh: command not found.')
        return responses
