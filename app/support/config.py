from typing import Dict, Any
import json

# noinspection PyUnresolvedReferences
import __main__ as main
from state import State
from .validation import validate_data


def load_config() -> Dict[str, Any]:
    """
    Load the configuration data and initializes the configuration paths.
    :return: The configuration data.
    """
    # Now load up the configuration data.
    with open(State.current.config_file_path) as config_file:
        config = json.load(config_file)
        validate_data(isinstance(config, dict), lambda: ValueError('Configuration root is not an object'))
        validate_data('switches' in config, lambda: KeyError('No switches defined'))
        validate_data('devices' in config, lambda: KeyError('No devices defined'))
        return config


def get_config_path(sub: str = '') -> str:
    """
    Resolves a configuration path.
    :param sub: If present, a relative from the configuration file to be resolved; otherwise, the base path is returned.
    :return:    The absolute resolved path.
    """
    return State.get_config_path(sub)
