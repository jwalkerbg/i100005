# core/config.py

import sys
from typing import Dict, Any
import argparse
import json
from jsonschema import validate, ValidationError
import importlib.resources as resources

from smartfan.logger import getAppLogger

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
            'template_version': "0.5.0",
            'template_description': { 'text': """Template with CLI interface, configuration options in a file, logger and unit tests""", 'content-type': "text/plain" }
        },
        'metadata': {
            'version': False
        },
        'logging': {
            'verbose': False
        },
        'mqttms': {
            'mqtt': {
                'host': 'localhost',
                'port': 1883,
                'username': 'guest',
                'password': 'guest',
                'client_id': 'mqttx_93919c20',
                "timeout": 15.0,
                "long_payload": 25
            },
            'ms': {
                'client_mac': '1234567890AB',
                'server_mac': '112233445566',
                'cmd_topic': '@/server_mac/CMD/format',
                'rsp_topic': '@/client_mac/RSP/format',
                'timeout': 5.0
            }
        }
    }

    # When adding / removing changing configuration parameters, change following validation approrpiately
    CONFIG_SCHEMA = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "metadata": {
                "type": "object",
                "properties": {
                    "version": {
                        "type": "boolean"
                    }
                },
                "additionalProperties": False
            },
            "logging": {
                "type": "object",
                "properties": {
                    "verbose": {
                        "type": "boolean"
                    }
                },
                "additionalProperties": False
            },
            "mqttms": {
                "type": "object",
                "properties": {
                    "mqtt": {
                        "type": "object",
                        "properties": {
                            "host": {"type": "string"},
                            "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                            "username": {"type": "string"},
                            "password": {"type": "string"},
                            "client_id": {"type": "string"},
                            "timeout": {"type": "number"},
                            "long_payload": {"type": "integer", "minimum": 10, "maximum": 32768}
                        },
                        "required": ["host", "port"]
                    },
                    "ms": {
                        "type": "object",
                        "properties": {
                            "client_mac": {"type": "string"},
                            "server_mac": {"type": "string"},
                            "cmd_topic": {"type": "string"},
                            "rsp_topic": {"type": "string"},
                            "timeout": {"type": "number"}
                        },
                        "required": ["client_mac", "server_mac", "cmd_topic", "rsp_topic", "timeout"]
                    }
                },
                "required": ["mqtt", "ms"],
                "additionalProperties": False
            }
        },
        "required": ["logging", "mqttms"],
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

        # Handle MQTT CLI overrides
        if config_cli:
            if config_cli.mqtt_host:
                self.config['mqttms']['mqtt']['host'] = config_cli.mqtt_host
            if config_cli.mqtt_port:
                self.config['mqttms']['mqtt']['port'] = config_cli.mqtt_port
            if config_cli.mqtt_username:
                self.config['mqttms']['mqtt']['username'] = config_cli.mqtt_username
            if config_cli.mqtt_password:
                self.config['mqttms']['mqtt']['password'] = config_cli.mqtt_password
            if config_cli.mqtt_client_id:
                self.config['mqttms']['mqtt']['client_id'] = config_cli.mqtt_client_id
            if config_cli.mqtt_timeout:
                self.config['mqttms']['mqtt']['timeout'] = config_cli.mqtt_timeout
            if config_cli.long_payload:
                self.config['mqttms']['mqtt']['long_payload'] = config_cli.long_payload

            # handle ms protocol overrides
            if config_cli.ms_client_mac:
                self.config['mqttms']['ms']['client_mac'] = config_cli.ms_client_mac
            if config_cli.ms_server_mac:
                self.config['mqttms']['ms']['server_mac'] = config_cli.ms_server_mac
            if config_cli.ms_cmd_topic:
                self.config['mqttms']['ms']['cmd_topic'] = config_cli.ms_cmd_topic
            if config_cli.ms_rsp_topic:
                self.config['mqttms']['ms']['rsp_topic'] = config_cli.ms_rsp_topic
            if config_cli.ms_timeout:
                self.config['mqttms']['ms']['timeout'] = config_cli.ms_timeout

            if config_cli.app_version:
                self.config['metadata']['version'] = True
            # Handle general options
            if config_cli.verbose:
                self.config['logging']['verbose'] = config_cli.verbose

        return self.config

    def log_configuration(self):
        logger.info("Running in verbose mode.")
        logger.info(f"Final Configuration: {self.config}")

        # MQTT configuration
        mqtt_config = self.config['mqttms']['mqtt']
        logger.info(f"MQTT Configuration:")
        logger.info(f"  Host: {mqtt_config['host']}")
        logger.info(f"  Port: {mqtt_config['port']}")
        logger.info(f"  Username: {mqtt_config.get('username', 'N/A')}")
        logger.info(f"  Password: {mqtt_config.get('password', 'N/A')}")
        logger.info(f"  Client ID: {mqtt_config.get('client_id', 'N/A')}")
        logger.info(f"  Timeout: {mqtt_config.get('timeout', 'N/A')}")
        logger.info(f"  Long payloads threshold: {mqtt_config.get('long_payload', 'N/A')}")

        ms_config = self.config['mqttms']['ms']
        logger.info(f"MS Configuration")
        logger.info(f"  Client (master) MAC: {ms_config.get('client_mac', 'N/A')}")
        logger.info(f"  Server (slave) MAC:  {ms_config.get('server_mac', 'N/A')}")
        logger.info(f"  Command topic:  {ms_config.get('cmd_topic', 'N/A')}")
        logger.info(f"  Response topic: {ms_config.get('rsp_topic', 'N/A')}")
        logger.info(f"  MS protocol timeout: {ms_config.get('timeout', 'N/A')}")

        logger.info("Application started with the above configuration...")
