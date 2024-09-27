# smartfan/core.py

import time
import struct
from typing import Dict
import mqttms
from mqttms.mqtt_handler import MQTTHandler
from mqttms.ms_protocol import MSProtocol
from mqttms.mqtt_dispatcher import MQTTDispatcher
from mqttms.core import graceful_exit
from smartfan.ms_host import MShost
from smartfan.config import merge_cli_options
from smartfan.logger_module import logger, string_handler

def run_app(config: Dict):
    """Run the application with the given configuration."""

    ms_protocol = None
    mqtt_dispatcher = None
    mqtt_handler = None

    try:
        ms_protocol = MSProtocol(config=config)
        mqtt_dispatcher = MQTTDispatcher(config=config, protocol=ms_protocol)
        mqtt_handler = MQTTHandler(config=config,message_handler=mqtt_dispatcher)
        ms_protocol.define_mqtt_handler(mqtt_handler)   # needed for publishing commands
    except Exception as e:
        logger.error(f"Cannot create MQTTHandler object: {e}")
        if mqtt_handler:
            mqtt_handler.exit_threads()
        return

    # connect broker
    try:
        res = mqtt_handler.connect()
        if not res:
            mqtt_handler.exit_threads()
            return
    except Exception as e:
        logger.error(f"Cannot connect to the MQTT broker: {e}")
        graceful_exit(ms_protocol, mqtt_handler)
        return

    # subscribe for MS protocol
    try:
        res = ms_protocol.subscribe(ms_protocol.construct_rsp_topic())
        if not res:
            logger.warning(f"CORE: Not successful subscription. Giving up")
            graceful_exit(ms_protocol,mqtt_handler)
            return
    except Exception as e:
        logger.error(f"Cannot subscribe to the MQTT broker: {e}")
        graceful_exit(ms_protocol,mqtt_handler)
        return

    ms_host = MShost(ms_protocol=ms_protocol,config=config)

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
                print(f"Version: {version}")
                print(f"Serial Number: {serial}")

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
        graceful_exit(ms_protocol,mqtt_handler)
        #ms_protocol.queue_cmd.put((None, None))
        #mqtt_handler.disconnect_and_exit()
        logger.warning("Application stopped by user (Ctrl-C). Exiting...")
