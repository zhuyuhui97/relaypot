import hashlib, json, os, random

from twisted.internet import protocol
from twisted.python import failure

from relaypot import utils
from relaypot.agent.base import BaseAgent


class Agent(BaseAgent):
    req_dict = None
    resp_dict = None
    STATUS_NO_AUTH = 0
    STATUS_REQ_USERNAME = 1
    STATUS_REQ_PASSWORD = 2
    STATUS_AUTH_DONE = 3

    def load_profile():
        req_path = os.path.join(utils.home_path, 'req.json')
        resp_path = os.path.join(utils.home_path, 'resp.json')
        with open(req_path, 'r') as req_file:
            Agent.req_dict = json.load(req_file)
        with open(resp_path, 'r') as resp_file:
            Agent.resp_dict = json.load(resp_file)

    
    def __init__(self, fproto:protocol.Protocol):
        self.fproto = fproto
        if Agent.req_dict == None or Agent.resp_dict == None:
            Agent.load_profile()
        return None

    def on_init(self):
        self.on_response([self.get_resp('WAIT')])

    def on_request(self, buf):
        bufhash = hashlib.md5(buf).hexdigest()
        self.on_response([self.get_resp(bufhash)])
        
    def get_resp(self, bufhash):
        if bufhash not in Agent.req_dict:
            bufhash = random.choice(list(Agent.req_dict.keys()))
        responses = Agent.req_dict[bufhash]['resp']
        resp_hash = random.choice(responses)
        resp = eval(Agent.resp_dict[resp_hash]['buf'])
        return resp