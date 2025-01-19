# testbench/tbench.py

import time
import struct
import re
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator, ValidationError

from smartfan.logger import get_app_logger
from smartfan.core import MShost

logger = get_app_logger(__name__)

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
    MOT_PHASE_FAST = 4
    MOT_PHASE_SLOW = 6
    MOT_STOP = 0

    def __init__(self, config: dict):
        self.config = config
        self.tests = [
                (self.t_who_am_i, "Who Am I" ),
                (self.t_version, "Version" ),
                (self.t_sensors, "Sensors" ),
                (self.t_motor, "Motor" ),
                (self.t_led, "Led"),
                (self.t_serialn, "Serial N")
            ]
        self.snonly = [
            (self.t_serialn, "Serial N")
        ]

    def set_ms_host(self, ms_host:MShost):
        self.ms_host = ms_host


    def ble_binding(self) -> bool :
        # Connect to BLE server, send Wifi, receive MAC
        # store MAC in config
        # subscribe MQTT
        # API_MQTT_READY

        # Replacement o fabove until it is coded with proper hadware BLE/serial module
        # Prompt the user for a MAC address
        mac_address = self.config["mqttms"]["ms"]["server_mac"]
        if self.config["options"]["interactive"]:
            mac_address = prompt('Enter a MAC address: ', default=mac_address, validator=MACAddressValidator())
        logger.error(f'Using MAC Address: {mac_address}')
        self.config["mqttms"]["ms"]["server_mac"] = mac_address

        return True

    def ms_subscribe(self):
        # subscribe to server topics
        try:
            res = self.ms_host.ms_protocol.subscribe()
            if not res:
                logger.error("Cannot subscribe to MQTT broker: %d",res)
                return
        except Exception as e:
            logger.error(f"Cannot subscribe to MQTT broker: {e}")
            return


    def run_tests(self):
        logger.info("TestBench.tests")

        self.ms_subscribe()

        if self.config["options"]["snonly"]:
            testarray = self.snonly
        else:
            if not self.config['options']['nopairing']:
                # This is called after succcessful binding and this command must be first one
                payload = self.ms_host.ms_wificred("*","*")
                if payload.get("response","") == "OK":
                    logger.info("WiFi credentials successfully cleared")
                else:
                    logger.info("WiFi credentials were not cleared")
                    # return

                payload = self.ms_host.ms_mqtt_ready()
                resp = payload.get("response","")
                if resp != "OK":
                    logger.error("API_MQTT_READY received answer: {resp}")
                    return
            testarray = self.tests

        for test in testarray:
            logger.info("")
            logger.info("**** Test %s ****",test[1])
            res = test[0]()
            if res:
                logger.info("**** Test %s: PASS",test[1])
            else:
                logger.info("**** Test %s: FAIL",test[1])
            if self.config['options']['stop_if_failed'] and not res:
                break

    # tests

    def t_who_am_i(self) -> bool:
        payload = self.ms_host.ms_who_am_i()
        if payload.get("response","") == "OK":
            jdata = payload.get('data', None)
            format_string = '<B'
            bdata = bytes.fromhex(jdata)
            unpacked_data = struct.unpack(format_string, bdata)
            logger.info("Device ID: %02x",unpacked_data[0])
            return True
        else:
            return False


    def t_version(self) -> bool:
        payload = self.ms_host.ms_version()
        if payload.get("response","") == "OK":
            jdata = payload.get('data', None)
            byte_array = bytes.fromhex(jdata)
            version_bytes, serial_bytes = byte_array.split(b'\0',1)
            versiondev = version_bytes.decode('ascii')
            serial = serial_bytes.decode('ascii').rstrip('\x00')
            logger.info(f"Version: %s",versiondev)
            logger.info("Serial Number: %s",serial)
            return True
        else:
            return False


    def t_sensors(self) -> bool:
        payload = self.ms_host.ms_sensors()
        if payload.get("response","") == "OK":
            jdata = payload.get('data', None)
            format_string = '<hIIIHBBB'
            bdata = bytes.fromhex(jdata)
            unpacked_data = struct.unpack(format_string, bdata)
            logger.info(f"MSH unpacked_data = {unpacked_data}")
            logger.info(f"\nTemperature: {unpacked_data[0]/100}\nPressure: {unpacked_data[1]/100} hPa\nHumidity: {unpacked_data[2]/1000} %\nGas:{unpacked_data[3]} Ohm\nAmbient light: {unpacked_data[4]}\nSensors: {unpacked_data[5]:x}\nMotor: {unpacked_data[6]:x}\nDevice state: {unpacked_data[7]:x}")
            return True
        else:
            logger.info("MSH: No valid data received")
            return False


    def t_motor(self) -> bool:
        motoron = self.config.get("tests").get("motoron", 3.0)
        motoroff = self.config.get("tests").get("motoroff", 1.0)
        self.ms_host.ms_motor(self.MOT_STOP)
        time.sleep(motoroff)
        self.ms_host.ms_motor(self.MOT_PHASE_SLOW)
        time.sleep(motoron)
        self.ms_host.ms_motor(self.MOT_STOP)
        time.sleep(motoroff)
        self.ms_host.ms_motor(self.MOT_PHASE_FAST)
        time.sleep(motoron)
        self.ms_host.ms_motor(self.MOT_STOP)
        time.sleep(motoroff)
        return True

    def t_led(self) -> bool:
        for _ in range(3):
            self.ms_host.ms_led(1)
            time.sleep(0.5)
            self.ms_host.ms_led(0)
            time.sleep(0.5)
        return True

    def t_serialn(self) -> bool:
        idn = self.config.get("dut").get("ident")
        serial_date = self.config.get("dut").get("serial_date")
        serialn = self.config.get("dut").get("serialn")
        serial_separator =  self.config.get("dut").get("serial_separator")
        snstr = idn + serial_separator + serial_date + serial_separator + serialn

        if self.config["options"]["interactive"]:
            snstr = prompt("Serial number: ", default=snstr)

        logger.info(f" S/N: %s",snstr)

        payload = self.ms_host.ms_serial(snstr)
        if payload.get("response","") == "OK":
            logger.info("Serial number is written")
            return True
        else:
            logger.info("Serial number was not set")
            return False
