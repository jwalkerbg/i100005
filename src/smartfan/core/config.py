# core/config.py

import sys
from typing import Dict, Any
import argparse
import json
from jsonschema import validate, ValidationError
import importlib.resources as resources

from pymodule.logger import getAppLogger

logger = getAppLogger(__name__)

# Check Python version at runtime
if sys.version_info >= (3, 11):
    import tomllib  # Use the built-in tomllib for Python 3.11+
else:
    import tomli  # Use the external tomli for Python 3.7 to 3.10

class Config:
    def __init__(self) -> None:
        self.config = self.DEFAULT_CONFIG

    DEFAULT_CONFIG = {
        'template': {
            'template_name': "pymodule",
            'template_version': "0.3.0",
            'template_description': { 'text': """Template with CLI interface, configuration options in a file, logger and unit tests""", 'content-type': "text/plain" }
        },
        'logging': {
            'verbose': True
        },
        'parameters': {
            'param1': 1,
            'param2': 2
        }
    }

    # When adding / removing changing configuration parameters, change following validation approrpiately
    CONFIG_SCHEMA = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "logging": {
                "type": "object",
                "properties": {
                    "verbose": {
                        "type": "boolean"
                    }
                },
                "additionalProperties": False
            },
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "number"
                    },
                    "param2": {
                        "type": "number"
                    }
                },
                "additionalProperties": False
            }
        },
        "additionalProperties": False
    }

    def load_toml(self,file_path) -> Dict:
        """
        Load a TOML file with exception handling.

        :param file_path: Path to the TOML file
        :return: Parsed TOML data as a dictionary
        :raises FileNotFoundError: If the file does not exist
        :raises tomli.TOMLDecodeError / tomllib.TOMLDecodeError: If there is a parsing error
        """
        try:
            # Open the file in binary mode (required by both tomli and tomllib)
            with open(file_path, 'rb') as f:
                if sys.version_info >= (3, 11):
                    return tomllib.load(f)  # Use tomllib for Python 3.11+
                else:
                    return tomli.load(f)  # Use tomli for Python 3.7 - 3.10

        except FileNotFoundError as e:
            logger.error(f"{e}")
            raise e  # Optionally re-raise the exception if you want to propagate it
        except (tomli.TOMLDecodeError if sys.version_info < (3, 11) else tomllib.TOMLDecodeError) as e:
            logger.error(f"Error: Failed to parse TOML file '{file_path}'. Invalid TOML syntax.")
            raise e  # Re-raise the exception for further handling
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading the TOML file: {e}")
            raise e  # Catch-all for any other unexpected exceptions

    def load_config_file(self, file_path: str="config.toml") -> Dict:
        # skip the configuration file if an empty name is given
        if file_path == '':
            return {}
        # Convert None to default value of 'config.json'
        if file_path is None:
            logger.error(f"CFG: Using default '{file_path}'")
            file_path = 'config.toml'
        try:
            config_file = self.load_toml(file_path=file_path)
            validate(instance=config_file, schema=self.CONFIG_SCHEMA)
        except ValidationError as e:
            logger.warning(f"Configuration validation error in {file_path}: {e}")
            raise ValueError
        except Exception as e:
            logger.error(f"Exception when trying to load {file_path}: {e}")
            raise e

        self.deep_update(config=self.config, config_file=config_file)

        return config_file

    def deep_update(self,config: Dict[str, Any], config_file: Dict[str, Any]) -> None:
        """
        Recursively updates a dictionary (`config`) with the contents of another dictionary (`config_file`).
        It performs a deep merge, meaning that if a key contains a nested dictionary in both `config`
        and `config_file`, the nested dictionaries are merged instead of replaced.

        Parameters:
        - config (Dict[str, Any]): The original dictionary to be updated.
        - config_file (Dict[str, Any]): The dictionary containing updated values.

        Returns:
        - None: The update is done in place, so the `config` dictionary is modified directly.
        """
        for key, value in config_file.items():
            if isinstance(value, dict) and key in config and isinstance(config[key], dict):
                # If both values are dictionaries, recurse to merge deeply
                self.deep_update(config[key], value)
            else:
                # Otherwise, update the key with the new value from config_file
                config[key] = value

    def merge_options(self, config_file:Dict, config_cli:argparse.Namespace=None) -> Dict:
        # handle CLI options if started from CLI interface
        # replace param1 and para2 with actual parameters, defined in app:parse_args()
        if config_cli:
            if config_cli.param1:
                self.config['parameters']['param1'] = config_cli.param1
            if config_cli.param2:
                self.config['parameters']['param2'] = config_cli.param2

            # Handle general options
            if config_cli.verbose is not None:
                self.config['logging']['verbose'] = config_cli.verbose

        return self.config
