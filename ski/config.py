'''

@author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
'''

import logging
import yaml

__DEFAULT_CONFIG = 'ski/conf/config.yaml'

# Set up logger
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Load config
with open(__DEFAULT_CONFIG, 'r') as f:
	log.info('Loading configuration from %s', __DEFAULT_CONFIG)
	config = yaml.load(f)


def __print_list(name, list):
	print('{0}={1}'.format(name, list))


def __print_string(name, val):
	print('{0}=\'{1}\''.format(name, val))


def __print_value(name, val):
	print('{0}={1}'.format(name, val))


def __print_dict(name, branch):
	kv = {
		dict : __print_dict
	  , list : __print_list
	  , str  : __print_string
	  , int  : __print_value
	  , bool : __print_value
	}

	for key in list(branch):
		val = branch[key]
		newkey = name + '.' + key
		kv[type(val)](newkey, val)


def dump_config():
	__print_dict('config', config)
