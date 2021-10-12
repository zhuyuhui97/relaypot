import yaml
import utils

def load_option(path):
    with open(path) as conffile:
        utils.global_config = yaml.load(conffile)
