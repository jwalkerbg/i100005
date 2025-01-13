# src/cli/app.py
import argparse
import time
from importlib.metadata import version
from typing import Dict, Tuple

from mqttms import MQTTms, MQTTDispatcher
# import smartfan.utils.utilities
from smartfan.core.config import Config
from smartfan.logger import get_app_logger
from smartfan.core.ms_host import MShost
from smartfan.testbench import TestBench

logger = get_app_logger(__name__)

class AppMQTTDispatcher(MQTTDispatcher):
    def __init__(self, config: Dict):
        super().__init__(config)

    def handle_message(self, message: Tuple[str, str]) -> bool:
        if not super().handle_message(message):
            logger.info(f"handle_message: -t '{message[0]}' -m '{message[1]}'")
            return True
        return False

def parse_args():
    """Parse command-line arguments, including nested options for mqtt and MS Protocol."""
    parser = argparse.ArgumentParser(description='Smartfan CLI application')

    # configuration file name
    parser.add_argument('--config', type=str, dest='config', default='config.toml',help="Name of the configuration file, default is 'config.toml'")
    parser.add_argument('--no-config', action='store_const', const='', dest='config', help="Do not use a configuration file (only defaults & options)")

    # version
    parser.add_argument('-v', dest='app_version', action='store_const', const=True, default=False, help='Show version information of the module')

    # Verbosity option
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument('--verbose', dest='verbose', action='store_const', const=True, help='Enable verbose mode')
    verbosity_group.add_argument('--no-verbose', dest='verbose', action='store_const', const=False, help='Disable verbose mode')

    # aplication options & parameters
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

    return parser.parse_args()

def main():
    """Main entry point of the CLI."""

    # Step 1: Create config object with default configuration
    cfg = Config()

    # Step 2: Parse command-line arguments
    args = parse_args()

    # Step 3: Try to load configuration from configuration file
    config_file = args.config
    try:
        cfg.load_config_file(config_file)
    except Exception:
        logger.info("Error with loading configuration file. Giving up.")
        return

    # Step 4: Merge default config, config.json, and command-line arguments
    cfg.merge_options(args)

    # Step 5: Run the application with collected configuration
    if cfg.config['metadata']['version']:
        app_version = version("smartfan")
        print(f"smartfan {app_version}")
    else:
        run_app(cfg)

# CLI application main function with collected options & configuration
def run_app(config:Config) -> None:

    print(f"config = {config.config}")

    try:
        logger.info("Running run_app")
        if config.config.get('logging').get('verbose', False):
            logger.info(f"config = {config.config}")

        # Create testBench object
        tb = TestBench(config.config)

        # Step 1) BLE binding, exchange WIFi credentials / MAC address
        if not tb.ble_binding():
            logger.error("Cannot bind with server via BLE")
            return

        # At this point:
        # Тhe server knows WiFi credentials and connects to MQTT broker
        # the client (this app) knows MAC address of the server

        # create MQTTms mqttms object to work with
        try:
            appdipatcher = AppMQTTDispatcher(config.config)
            mqttms = MQTTms(config.config['mqttms'],config.config['logging'],appdipatcher)
        except Exception as e:
            logger.error(f"Cannot create MQTTMS object. Giving up: {e}")
            return

        # connect broker
        try:
            res = mqttms.connect_mqtt_broker()
            if not res:
                mqttms.graceful_exit()
                return
        except Exception as e:
            mqttms.graceful_exit()
            logger.error(f"Cannot connect to MQTT broker: {e}.")
            return

        # create ms_host object if all above went well
        ms_host = MShost(ms_protocol=mqttms.ms_protocol,config=config)

        tb.set_ms_host(ms_host=ms_host)

        # Wait for a while to give the server chance to connecet to WhiFI and MQTT broker
        time.sleep(0.5)

        tb.run_tests()

    except KeyboardInterrupt:
        logger.warning("Application stopped by user (Ctrl-C). Exiting...")

    finally:
        # Graceful exit on Ctrl-C
        mqttms.graceful_exit()
        logger.info("Exiting run_app")

if __name__ == "__main__":
    main()
