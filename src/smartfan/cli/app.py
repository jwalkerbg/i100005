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
    mqtt_group = parser.add_argument_group('MQTT Options')
    mqtt_group.add_argument('--mqtt-host', type=str, help='MQTT host to connect to')
    mqtt_group.add_argument('--mqtt-port', type=int, help='MQTT port')
    mqtt_group.add_argument('--mqtt-username', type=str, help='MQTT username')
    mqtt_group.add_argument('--mqtt-password', type=str, help='MQTT password')
    mqtt_group.add_argument('--mqtt-client-id', type=str, help="MQTT Client ID, used by the broker")
    mqtt_group.add_argument("--mqtt-timeout", type=float, help="Timeout to wait connection or other activity in MQTT handler.")
    mqtt_group.add_argument("--mqtt-lp", type=int, dest='long_payload', help="Determines threshold of long payloads. When they are longer that this value, a short string is logged instead of real payloads. --verbose makes real payloads to be logged always.")

    # ms protocol
    ms_group = parser.add_argument_group('MS Protocol Options')
    ms_group.add_argument("--ms-client_mac", type=str, dest='ms_client_mac', help="MAC address of the client (master side).")
    ms_group.add_argument("--ms-server_mac", type=str, dest='ms_server_mac', help="MAC address of the server (slave side).")
    ms_group.add_argument("--ms-cmd-topic", type=str, dest='ms_cmd_topic', help="Template of command topic.")
    ms_group.add_argument("--ms-rsp-topic", type=str, dest='ms_rsp_topic', help="Template of response topic.")
    ms_group.add_argument("--ms-timeout", type=float, dest='ms_timeout', help="Timeout used in protocol to wait for response.")

    # dut
    dut_group = parser.add_argument_group('DUT Data')
    dut_group.add_argument("--dut-ident", type=str, dest='dut_ident', help="ID Number of Device Under Test")
    dut_group.add_argument("--dut-name", type=str, dest='dut_name', help="Device name")
    dut_group.add_argument("--dut-serial-date", type=str, dest='dut_serial_date', help="Date as part of serial number")
    dut_group.add_argument("--dut-serialn", type=str, dest='dut_serialn', help="Serial number of the Device Under Test")
    dut_group.add_argument("--dut-sn-separator", type=str, dest='serial_separator', help="Separator string or symbol used to separate parts of the serial number")

    # tests
    tests_group = parser.add_argument_group('Tests Options')
    tests_group.add_argument("--motoron", type=float, dest='motoron', help="Time to maintain motor enabled in tests")
    tests_group.add_argument("--motoroff", type=float, dest='motoroff', help="Time to maintain motor disabled in tests")

    # operative options
    operative_group = parser.add_argument_group('Operative Options')
    operative_group.add_argument("--sn-only", dest='snonly', action='store_const', const=True, default=False, help="Write only serial number without any tests. Expects device with valid WiFi credentials, connected to the Internet. Activates --no-pairing option.")
    operative_group.add_argument("--dut-delay", type=float, dest='dutdelay', help="Delay after BLE pairing and connecting to MQTT before start of tests driven by MS protocol over MQTT. This time allows DUT to setup WiFi/MQTT connection.")
    interactive_group = operative_group.add_mutually_exclusive_group()
    interactive_group.add_argument('--interactive', dest='interactive', action='store_const', const=True, help='Enable interactive mode (default)')
    interactive_group.add_argument('--no-interactive', dest='interactive', action='store_const', const=False, help='Disable interactive mode')
    operative_group.add_argument("--stop-if-failed", dest='stop_if_failed', action='store_const', const=True, help="Stop execution of tests if current test failed")

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

    if cfg.config['options']['snonly']:
         cfg.config['options']['nopairing'] = True

    # Step 5: Run the application with collected configuration
    if cfg.config['metadata']['version']:
        app_version = version("smartfan")
        print(f"smartfan {app_version}")
    else:
        run_app(cfg)

# CLI application main function with collected options & configuration
def run_app(config:Config) -> None:

    try:
        logger.info("Running run_app")
        if config.config.get('logging').get('verbose', False):
            logger.info(f"config = {config.config}")

        # Create testBench object
        tb = TestBench(config.config)

        # Step 1) BLE binding, exchange WIFi credentials / MAC address
        if config.config['options']['nopairing']:
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

        # Wait for a while to give the server chance to connecet to WiFi and MQTT broker
        time.sleep(config.config['options']['dutdelay'])

        tb.run_tests()

    except KeyboardInterrupt:
        logger.warning("Application stopped by user (Ctrl-C). Exiting...")

    finally:
        # Graceful exit on Ctrl-C
        if 'mqttms' in locals():
            mqttms.graceful_exit()
        logger.info("Exiting run_app")

if __name__ == "__main__":
    main()
