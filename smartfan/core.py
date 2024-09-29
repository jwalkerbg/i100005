# smartfan/core.py

import time
import struct
from typing import Dict
from mqttms import MQTTMS
from smartfan.ms_host import MShost
from smartfan.config import merge_cli_options
from smartfan.logger_module import logger, string_handler

def run_app(config: Dict):
    """Run the application with the given configuration."""

    try:
        mqttms = MQTTMS(config)
    except Exception as e:
        logger.error(f"Cannot create MQTTMS object. Giving up: {e}")
        return

    try:
        res = mqttms.connect_mqtt_broker()
        if not res:
            mqttms.graceful_exit()
            return
    except Exception as e:
        mqttms.graceful_exit()
        logger.error(f"Cannot connect to MQTT broker: {e}.")
        return

    try:
        res = mqttms.subscribe()
        if not res:
            logger.error(f"Cannot subscribe to MQTT broker.")
            return
    except Exception as e:
        logger.error(f"Cannot subscribe to MQTT broker: {e}")
        return

    ms_host = MShost(ms_protocol=mqttms.ms_protocol,config=config)

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
