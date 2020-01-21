"""
  Loads and manages configuration data.
"""

import logging
import yaml

__DEFAULT_CONFIG = 'ski/conf/config.yaml'

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def __print_list(name, val):
    print('{0}={1}'.format(name, val))


def __print_string(name, val):
    print('{0}=\'{1}\''.format(name, val))


def __print_value(name, val):
    print('{0}={1}'.format(name, val))


def __print_dict(name, branch):
    kv = {
        dict: __print_dict,
        list: __print_list,
        str: __print_string,
        int: __print_value,
        bool: __print_value
    }

    for key in list(branch):
        val = branch[key]
        new_key = name + '.' + key
        kv[type(val)](new_key, val)


def dump_config():
    """Print the configuration to the console."""
    __print_dict('config', config)


def load_config(file_name):
    """Load configuration from the specified YAML file."""
    with open(file_name, 'r') as f:
        log.info('Loading configuration from %s', file_name)
        return yaml.load(f)


# Load default config
config = load_config(__DEFAULT_CONFIG)
