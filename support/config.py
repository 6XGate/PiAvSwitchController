# noinspection PyUnresolvedReferences
import __main__ as main
import os
import json
from typing             import Dict, Any
from support.validation import validate_data

# The path to the main program.
program_path = str()
# The path to the directory containing the main program.
program_dir  = str()
# The path to the configuration file.
config_path  = str()
# The path to the directory containing the configuration file.
config_dir   = str()

def load_config() -> Dict[str, Any]:
    """
    Load the configuration data and initializes the configuration paths.
    :return: The configuration data.
    """
    global program_path, program_dir, config_path, config_dir

    # Initialize the configuration paths or path resolution.
    program_path = os.path.abspath(str(main.__file__))
    program_dir  = os.path.dirname(program_path)
    config_path  = os.path.abspath(os.path.join(program_dir, './config/pigaswi.json'))
    config_dir   = os.path.dirname(config_path)

    # Now load up the configuration data.
    with open(config_path) as config_file:
        config = json.load(config_file)
        validate_data(isinstance(config, dict), lambda: ValueError('Configuration root is not an object'))
        validate_data('switches' in config,     lambda: KeyError('No switches defined'))
        validate_data('devices' in config,      lambda: KeyError('No devices defined'))
        return config

def get_app_path(sub: str = '') -> str:
    """
    Resolves an application path.
    :param sub: If present, a relative from the application path to be resolved; otherwise, the base path is returned.
    :return:    The absolute resolved path.
    """
    global program_dir

    return os.path.abspath(os.path.join(program_dir, sub))

def get_config_path(sub: str = '') -> str:
    """
    Resolves a configuration path.
    :param sub: If present, a relative from the configuration file to be resolved; otherwise, the base path is returned.
    :return:    The absolute resolved path.
    """
    global config_dir

    return os.path.abspath(os.path.join(config_dir, sub))
