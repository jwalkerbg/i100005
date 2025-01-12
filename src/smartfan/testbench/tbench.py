# testbench/tbench.py

import struct

from mqttms import MQTTms

from smartfan.logger import getAppLogger
from smartfan.core import MShost

logger = getAppLogger(__name__)

from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError
import re

class MACAddressValidator(Validator):
    def validate(self, document):
        # Regular expression for a valid MAC address (12 hex characters)
        mac_regex = r'[0-9a-fA-F]{12}'
        if not re.fullmatch(mac_regex, document.text):
            raise ValidationError(
                message='Invalid MAC address. Please enter exactly 12 hex characters (0-9, a-f, A-F) without symbols.',
                cursor_position=len(document.text)  # Move cursor to the end
            )


class TestBench:
    def __init__(self, config: dict):
        self.config = config


    def set_ms_mqtt(self, ms_host:MShost, mqttms:MQTTms):
        self.ms_host = ms_host
        self.mqttms=mqttms


    def ble_binding(self) -> bool :
        # Connect to BLE server, send Wifi, receive MAC
        # store MAC in config
        # subscribe MQTT
        # API_MQTT_READY

        # Replacement o fabove until it is coded with proper hadware BLE/serial module
        # Prompt the user for a MAC address
        mac_address = prompt('Enter a MAC address: ', default=self.config["mqttms"]["ms"]["server_mac"], validator=MACAddressValidator())
        print(f'Validated MAC Address: {mac_address}')
        self.config["mqttms"]["ms"]["server_mac"] = mac_address

        return True

    def ms_subscribe(self):
        # subscribe to server topics
        try:
            logger.info(f"ms_subscribe topic: %s",self.mqttms.ms_protocol.config)
            res = self.mqttms.subscribe()
            if not res:
                logger.error(f"Cannot subscribe to MQTT broker.")
                return
        except Exception as e:
            logger.error(f"Cannot subscribe to MQTT broker: {e}")
            return


    def tests(self):
        logger.info("TestBench.tests")

        self.ms_subscribe()

        # This is called after succcessful binding o this command must be first one

        payload = self.ms_host.ms_mqtt_ready()
        resp = payload.get("response","")
        if resp != "OK":
            logger.error("API_MQTT_READy received answer: {resp}")
            return

        self.t_who_am_i()
        self.t_version()
        self.t_sensors()

    def t_who_am_i(self):
        payload = self.ms_host.ms_who_am_i()


    def t_version(self):
        payload = self.ms_host.ms_version()
        if payload.get("response","") == "OK":
            jdata = payload.get('data', None)
            byte_array = bytes.fromhex(jdata)
            version_bytes, serial_bytes = byte_array.split(b'\0',1)
            versiondev = version_bytes.decode('ascii')
            serial = serial_bytes.decode('ascii').rstrip('\x00')
            logger.info(f"Version: {versiondev}")
            logger.info(f"Serial Number: {serial}")


    def t_led(self):
        pass

    def t_motor(self):
        pass

    def t_sensors(self):
        payload = self.ms_host.ms_sensors()
        if payload.get("response","") == "OK":
            jdata = payload.get('data', None)
            format_string = '<hIIIHBBB'
            bdata = bytes.fromhex(jdata)
            unpacked_data = struct.unpack(format_string, bdata)
            logger.info(f"MSH unpacked_data = {unpacked_data}")
        else:
            logger.info("MSH: No valid data received")






