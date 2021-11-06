import os
import string
import random
import itertools
from agent.base import BaseAgent


class Agent(BaseAgent):
    STATUS_REQ_USERNAME = 0
    STATUS_REQ_PASSWORD = 1
    STATUS_REQ_COMMAND = 2
    NON_PRINTABLE = itertools.chain(range(0x00, 0x20), range(0x7f, 0xa0))

    def __init__(self, profile_name=None, profile_base='profiles'):
        plist = os.listdir(profile_base)
        if profile_name == None:
            rnd = random.randrange(0, len(plist))
            self.profile_name = plist[rnd]
        else:
            self.profile_name = profile_name
        self.profile_base = profile_base
        self.load_profile()
        self.status = self.STATUS_REQ_USERNAME

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
            return [self.get_resp(buf), '\n', self.ps]

    def get_resp(self, buf):
        # TODO How to display commands when there are non-unicode bytes?
        return 'sh: command not found.'
