import os
import random
import itertools
import subprocess

from twisted.internet import protocol
from twisted.python import failure

from relaypot.agent.base import BaseAgent


class Agent(BaseAgent):
    STATUS_NO_AUTH = 0
    STATUS_REQ_USERNAME = 1
    STATUS_REQ_PASSWORD = 2
    STATUS_AUTH_DONE = 3
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
        self.status = self.STATUS_NO_AUTH
        self.line_buffer = b''
    
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
            self.ps1 = b'? '
            self.ps2 = b'> '
            self.ps = self.ps1
            while True:
                line = pfile.readline()
                if line == '':
                    break

    def on_init(self):
        self.status = self.STATUS_REQ_USERNAME
        return [b'\xff\xfd\x01\xff\xfd\x1f\xff\xfb\x01\xff\xfb\x03R6300V2-14EF login: ']

    # def on_request(self, buf:bytes):
    #     self.line_buffer = self.line_buffer.join(buf)
    #     if self.status == self.STATUS_NO_AUTH:
    #         pass # TODO Username sent without any probe
    #     if self.status == self.STATUS_REQ_USERNAME:
    #         self.status = self.STATUS_REQ_PASSWORD
    #         self.username = buf.strip()
    #         return [self.username, '\r\nPassword: ']
    #     elif self.status == self.STATUS_REQ_PASSWORD:
    #         self.status = self.STATUS_AUTH_DONE
    #         return [b'\r\n\r\n\r\nASUSWRT-Merlin R6300V2 380.70-0-X7.9.1 Tue Sep 25 11:47:13 UTC 2018\r\n', self.ps1]
    #     else:
    #         resp = [buf] # echo
    #         if self.line_buffer.endswith(b'\r\n'):
    #             resp.extend(self.get_resp(self.line_buffer))
    #             self.line_buffer = b''
    #             resp.append(self.ps)
    #         return resp

    def on_request(self, buf:bytes):
        self.line_buffer = self.line_buffer.join(buf)
        if self.status == self.STATUS_REQ_PASSWORD:
            resp = [] # No echo when input password
        else:
            resp = [buf] # Echo
        
        if self.line_buffer.endswith(b'\r\n'):
            if self.status == self.STATUS_NO_AUTH:
                pass # TODO Username sent without any probe
            elif self.status == self.STATUS_REQ_USERNAME:
                self.status = self.STATUS_REQ_PASSWORD
                self.username = buf.strip()
                resp.append('\r\nPassword: ')
            elif self.status == self.STATUS_REQ_PASSWORD:
                self.status = self.STATUS_AUTH_DONE
                resp.append(b'\r\n\r\n\r\nASUSWRT-Merlin R6300V2 380.70-0-X7.9.1 Tue Sep 25 11:47:13 UTC 2018\r\n')
                resp.append(self.ps1)
            else:
                if self.line_buffer.endswith(b'\r\n'):
                    resp.extend(self.get_resp(self.line_buffer))
                    self.line_buffer = b''
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
            elif b'echo' in cmd:
                subp = subprocess.run(cmd,stdout=subprocess.PIPE, shell=True)
                subp.check_returncode()
                responses.append(subp.stdout)
            else:
                responses.append(b'sh: command not found.')
        return responses
