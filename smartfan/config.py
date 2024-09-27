import os
from typing import Dict, Any  # Import only the necessary types
import json
from jsonschema import validate, ValidationError
from mqttms import config
from smartfan.logger_module import logger, string_handler

def merge_cli_options(config:Dict, config_cli=None):

    # Handle MQTT CLI overrides
    if config_cli:
        if config_cli.mqtt_host:
            config['mqtt']['host'] = config_cli.mqtt_host
        if config_cli.mqtt_port:
            config['mqtt']['port'] = config_cli.mqtt_port
        if config_cli.mqtt_username:
            config['mqtt']['username'] = config_cli.mqtt_username
        if config_cli.mqtt_password:
            config['mqtt']['password'] = config_cli.mqtt_password
        if config_cli.mqtt_client_id:
            config['mqtt']['client_id'] = config_cli.mqtt_client_id
        if config_cli.mqtt_timeout:
            config['mqtt']['timeout'] = config_cli.mqtt_timeout
        if config_cli.long_payload:
            config['mqtt']['long_payload'] = config_cli.long_payload

        # handle ms protocol overrides
        if config_cli.ms_client_mac:
            config['ms']['client_mac'] = config_cli.ms_client_mac
        if config_cli.ms_server_mac:
            config['ms']['server_mac'] = config_cli.ms_server_mac
        if config_cli.ms_cmd_topic:
            config['ms']['cmd_topic'] = config_cli.ms_cmd_topic
        if config_cli.ms_rsp_topic:
            config['ms']['rsp_topic'] = config_cli.ms_rsp_topic
        if config_cli.ms_timeout:
            config['ms']['timeout'] = config_cli.ms_timeout

        # Handle general options
        if config_cli.verbose is not None:
            config['verbose'] = config_cli.verbose

    # Print verbose mode status
    if config.get('verbose'):
        log_configuration(config)

    return config

def log_configuration(config):
    logger.info("Running in verbose mode.")
    logger.info(f"Final Configuration: {config}")

    # MQTT configuration
    mqtt_config = config['mqtt']
    logger.info(f"MQTT Configuration:")
    logger.info(f"  Host: {mqtt_config['host']}")
    logger.info(f"  Port: {mqtt_config['port']}")
    logger.info(f"  Username: {mqtt_config.get('username', 'N/A')}")
    logger.info(f"  Password: {mqtt_config.get('password', 'N/A')}")
    logger.info(f"  Client ID: {mqtt_config.get('client_id', 'N/A')}")
    logger.info(f"  Timeout: {mqtt_config.get('timeout', 'N/A')}")
    logger.info(f"  Long payloads threshold: {mqtt_config.get('long_payload', 'N/A')}")

    ms_config = config['ms']
    logger.info(f"MS Configuration")
    logger.info(f"  Client (master) MAC: {ms_config.get('client_mac', 'N/A')}")
    logger.info(f"  Server (slave) MAC:  {ms_config.get('server_mac', 'N/A')}")
    logger.info(f"  Command topic:  {ms_config.get('cmd_topic', 'N/A')}")
    logger.info(f"  Response topic: {ms_config.get('rsp_topic', 'N/A')}")
    logger.info(f"  MS protocol timeout: {ms_config.get('timeout', 'N/A')}")

    logger.info("Application started with the above configuration...")
