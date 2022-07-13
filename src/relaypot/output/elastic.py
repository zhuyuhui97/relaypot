from typing import Any, Dict
from ssl import create_default_context
from os import path

from elasticsearch import Elasticsearch, NotFoundError

from relaypot import utils
from relaypot.output import null


class Writer(null.Writer):
    EV_CLI_SYN = 'relaypot.session.connected'
    EV_CLI_FIN = 'relaypot.session.disconnected'
    EV_SRV_RST = 'relaypot.session.srv_reset'
    EV_CLI_REQ = 'relaypot.session.request'
    EV_SRV_RSP = 'relaypot.session.response'
    EV_CLI_DL = 'relaypot.file.download'
    EV_CLI_UL = 'relaypot.file.upload'

    index: str = 'relaypot_test'
    pipeline: str = 'geoip'
    es: Any

    @staticmethod
    def pre_init():
        if utils.global_config == None:
            # TODO raise another exception
            raise Exception

        config = utils.global_config['backend']['es']
        host = config['host']
        port = str(config['port'])
        Writer.index = config['index']

        ca_path = path.join('etc', 'elasticsearch-ca.pem')

        es_options: Dict[str, Any] = {
            # 'api_key' : ('Cf1wb3wB5zhXXict03zUA', 'G1NJYETDRayiIUIudt1ZR'),
            'ssl_show_warn': False,
            'verify_certs': False,
            'ca_certs': ca_path
        }
        config_keys = config.keys()
        if 'auth_id' in config_keys and 'auth_apikey' in config_keys:
            es_options['api_key'] = (config['auth_id'], config['auth_apikey'])
        elif 'auth_user' in config_keys and 'auth_pw' in config_keys:
            es_options['http_auth'] = (config['auth_user'], config['auth_pw'])
        else:  # TODO raise another exception
            raise Exception

        Writer.es = Elasticsearch(f'{host}:{port}', **es_options)

    def __init__(self, sid: str, sess) -> None:
        super().__init__(sid, sess)
        self.es = Writer.es

    def write(self, logentry):
        self.es.index(
            index=self.index, body=logentry, pipeline=self.pipeline
        )

    def check_geoip(self):
        pass
