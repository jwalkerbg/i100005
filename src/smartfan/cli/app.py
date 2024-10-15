# src/cli/app.py
import argparse
import time

from mqttms import MQTTms
import smartfan.utils.utilities
from smartfan.core.config import Config
from smartfan.logger import getAppLogger
from smartfan.core.ms_host import MShost

logger = getAppLogger(__name__)

def parse_args():
    """Parse command-line arguments, including nested options for mqtt and MS Protocol."""
    parser = argparse.ArgumentParser(description='Smartfan CLI application')

    # configuration file name
    parser.add_argument('--config', type=str, dest='config', default='config.toml',help="Name of the configuration file, default is 'config.toml'")
    parser.add_argument('--no-config', action='store_const', const='', dest='config', help="Do not use a configuration file (only defaults & options)")

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
    except Exception as e:
        logger.info(f"Error with loading configuration file. Giving up.")
        return

    # Step 4: Merge default config, config.json, and command-line arguments
    cfg.merge_options(cfg.config, args)

    # Step 5: Run the application with collected configuration
    run_app(cfg)

# CLI application main function with collected options & configuration
def run_app(config:Config) -> None:
    try:
        logger.info("Running run_app")
        if config.config.get('logging').get('verbose', False):
            logger.info(f"config = {config.config}")

        # create object
        try:
            mqttms = MQTTms(config.config['mqttms'],config.config['logging'])
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

        # subscribe
        try:
            res = mqttms.subscribe()
            if not res:
                logger.error(f"Cannot subscribe to MQTT broker.")
                return
        except Exception as e:
            logger.error(f"Cannot subscribe to MQTT broker: {e}")
            return

        # create ms_host object if all above went well
        ms_host = MShost(ms_protocol=mqttms.ms_protocol,config=config)

        # main loop of the program
        try:
            while True:
                # Simulate doing some work (replace this with actual logic)
                # payload = ms_host.ms_sensors()
                # if payload.get("response","") == "OK":
                #     jdata = payload.get('data', None)
                #     format_string = '<hIIIHBBB'
                #     bdata = bytes.fromhex(jdata)
                #     unpacked_data = struct.unpack(format_string, bdata)
                #     logger.info(f"MSH unpacked_data = {unpacked_data}")
                # else:
                #     logger.info("MSH: No valid data received")

                payload = ms_host.ms_who_am_i()

                payload = ms_host.ms_version()
                if payload.get("response","") == "OK":
                    jdata = payload.get('data', None)
                    byte_array = bytes.fromhex(jdata)
                    version_bytes, serial_bytes = byte_array.split(b'\0',1)
                    version = version_bytes.decode('ascii')
                    serial = serial_bytes.decode('ascii').rstrip('\x00')
                    logger.info(f"Version: {version}")
                    logger.info(f"Serial Number: {serial}")

                # payload = ms_host.ms_serial("2407-0002")

                # payload = ms_host.ms_wificred("iv_cenov", "6677890vla")

                # payload = ms_host.ms_get_params()

                # payload = ms_host.ms_set_mode(0)
                # payload = ms_host.ms_set_amb_thr(1024)
                # payload = ms_host.ms_set_hum_thr(75)
                # payload = ms_host.ms_set_hum_thr(100)

                # payload = ms_host.ms_set_gas_thr(16000)
                # payload = ms_host.ms_set_gas_thr(50000)

                # payload = ms_host.ms_set_forced_time(25)
                # payload = ms_host.ms_set_forced_time(61)

                time.sleep(5)  # Sleep to avoid busy-waiting
        except KeyboardInterrupt:
            # Graceful exit on Ctrl-C
            mqttms.graceful_exit()
            logger.warning("Application stopped by user (Ctrl-C). Exiting...")

############################
        # smartfan.core.core_module_a.hello_from_core_module_a()
        # smartfan.core.core_module_a.goodbye_from_core_module_a()
        # smartfan.core.core_module_b.hello_from_core_module_b()
        # smartfan.core.core_module_b.goodbye_from_core_module_b()
        # smartfan.utils.hello_from_utils()
        # smartfan.drivers.hello_from_ina236()
############################

    finally:
        logger.info("Exiting run_app")

if __name__ == "__main__":
    main()
