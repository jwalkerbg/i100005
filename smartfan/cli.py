import argparse
import logging
import mqttms
from mqttms import config

from smartfan.core import run_app
from smartfan.config import merge_cli_options
from smartfan.logger_module import logger, string_handler

def parse_args():
    """Parse command-line arguments, including nested options for mqtt and MS Protocol."""
    parser = argparse.ArgumentParser(description='My CLI App with Config File and Overrides')

    # MQTT options
    parser.add_argument('--mqtt-host', type=str, help='MQTT host to connect to')
    parser.add_argument('--mqtt-port', type=int, help='MQTT port')
    parser.add_argument('--mqtt-username', type=str, help='MQTT username')
    parser.add_argument('--mqtt-password', type=str, help='MQTT password')
    parser.add_argument('--mqtt-client-id', type=str, help="MQTT Client ID, used by the broker")
    parser.add_argument("--mqtt-timeout", type=float, help="Timeout to wait connection or other activity in MQTT handler.")
    parser.add_argument("--mqtt-lp", type=int, dest='long_payload', help="Determines threshold of long payloads. When they are longer that this value, a short string is logged instead of real payloads. --verbose makes real payloads to be logged always.")

    # ms protocol
    parser.add_argument("--ms-client_mac", type=str, dest='ms_client_mac', help="MAC address of the client (master side).")
    parser.add_argument("--ms-server_mac", type=str, dest='ms_server_mac', help="MAC address of the server (slave side).")
    parser.add_argument("--ms-cmd-topic", type=str, dest='ms_cmd_topic', help="Template of command topic.")
    parser.add_argument("--ms-rsp-topic", type=str, dest='ms_rsp_topic', help="Template of response topic.")
    parser.add_argument("--ms-timeout", type=float, dest='ms_timeout', help="Timeout used in protocol to wait for response.")

    # Other general options can still be added
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument('--verbose', dest='verbose', action='store_const', const=True, help='Enable verbose mode')
    verbosity_group.add_argument('--no-verbose', dest='verbose', action='store_const', const=False, help='Disable verbose mode')

    return parser.parse_args()

def main():
    """Main entry point of the CLI."""

    mqttms_logger = logging.getLogger('mqttms')
    mqttms_logger.propagate = False
    mqttms_logger.setLevel(logging.INFO)

    # Step 0: Log the beginning
    logger.info("mqttms beginning")

    # Step 1: Load the default configuration from config.json
    config_file = config.load_config()

    # Step 2: Parse command-line arguments
    args = parse_args()

    # Step 3: Merge default config, config.json, and command-line arguments
    final_config = merge_cli_options(config_file, args)

    # Step 4: Run the application using the final configuration
    run_app(final_config)

    # Step 6: Final message
    logger.info("mqttms end")

if __name__ == "__main__":
    main()
