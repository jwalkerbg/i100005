# testbench/tbench.py

import time
import struct
import re
import logging
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
    MOT_RUNNING = 1
    MOT_PHASE_FAST = 4
    MOT_PHASE_SLOW = 6
    MOT_STOP = 0

    SEN_HUMIDITY = 1
    SEN_AIR = 2
    SEN_AMBIENT = 4

    DEV_STATE_MASK = 0x07
    DEV_STATE_READY = 0x00
    DEV_STATE_NORMAL = 0x01
    DEV_STATE_FORCED = 0x02
    DEV_STATE_LOCAL = 0x08
    DEV_WIFI_CONNECTED = 0x10
    DEV_MQTT_SUBSCRIBED = 0x20

    def __init__(self, config: dict):
        self.config = config
        self.tests = [
                (self.t_who_am_i, "Who Am I" ),
                (self.t_version, "Version" ),
                (self.t_testmode, "Test Mode" ),
                (self.t_sensors, "Sensors" ),
                (self.t_motor, "Motor" ),
                (self.t_led, "Led"),
                (self.t_serialn, "Serial N")
            ]
        self.snonly = [
            (self.t_serialn, "Serial N")
        ]
        self.monitor = [
            (self.t_monitor, "Monitor")
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
        logger.info("Using MAC Address: %s", mac_address)
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

        match self.config["options"]["mode"]:
            case "snonly":
                testarray = self.snonly
            case "monitor":
                testarray = self.monitor
            case "testbench":
                testarray = self.tests

        if not self.config['options']['nopairing']:
            # This is called after succcessful binding and this command must be first one
            if not self.config['options']['noresetwifi']:
                payload = self.ms_host.ms_wificred("*","*")
                if payload.get("response","") == "OK":
                    logger.info("WiFi credentials successfully cleared")
                else:
                    logger.info("WiFi credentials were not cleared")
                    return

            payload = self.ms_host.ms_mqtt_ready()
            resp = payload.get("response","")
            if resp != "OK":
                logger.error("API_MQTT_READY received answer: {resp}")
                return

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
        return False


    def t_testmode(self) -> bool:
        payload = self.ms_host.ms_testmode()
        if payload.get("response","") == "OK":
            logger.info("Test mode is set")
            return True
        logger.info("Test mode was not set")
        return False


    def t_sensors(self) -> bool:
        sensor_data = self.read_sensors()
        if sensor_data:
            logger.info(f"MSH sensor_data = {sensor_data}")
            self.print_sensor_data(sensor_data)
            return True
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

        logger.info(" S/N: %s",snstr)

        payload = self.ms_host.ms_serial(snstr)
        if payload.get("response","") == "OK":
            logger.info("Serial number is written")
            return True

        logger.info("Serial number was not set")
        return False

    def t_monitor(self):
        logger.info("Press Ctrl+C to stop monitoring")
        logger.setLevel(logging.WARNING)
        logging.getLogger("smartfan.core.ms_host").setLevel(logging.WARNING)
        logging.getLogger("mqttms").setLevel(logging.WARNING)
        print('\n')
        try:
            count = 0
            lines = 0
            monitor_loops = self.config["options"]["monitor_loops"]
            while True:
                print(f"Monitoring loop: {count + 1}")
                lines = 1
                sensor_data = self.read_sensors()
                if sensor_data:
                    lines += self.print_sensor_data(sensor_data)
                else:
                    print("No valid data received")
                    lines += 1

                count += 1
                if monitor_loops != 0 and count >= monitor_loops:
                    break

                time.sleep(self.config["options"]["monitor_delay"])
                print(f"\033[{lines}A", end="", flush=True)
        except KeyboardInterrupt as e   :
            raise e
        finally:
            logger.setLevel(logging.INFO)
            logging.getLogger("smartfan.core.ms_host").setLevel(logging.INFO)
            logging.getLogger("mqttms").setLevel(logging.INFO)
            print('')
            logger.info("Monitoring stopped")

        return True

    def read_sensors(self):
        payload = self.ms_host.ms_sensors()
        if payload.get("response","") == "OK":
            jdata = payload.get('data', None)
            format_string = '<hIIIHBBB'
            bdata = bytes.fromhex(jdata)
            unpacked_data = struct.unpack(format_string, bdata)
            return unpacked_data
        return None

    def print_sensor_data(self, sensor_data):
        temperature, pressure, humidity, gas, light, sensors, motor, state = sensor_data

        print(f"\033[KTemperature: {temperature/100:.2f} °C")
        print(f"\033[KPressure: {pressure/100:.2f} hPa")
        print(f"\033[KHumidity: {humidity/1000:.2f} %")
        print(f"\033[KGas: {gas} Ohm")
        print(f"\033[KAmbient light: {light}")
        print(f'\033[KSensors: {sensors:x}: Ambient light: {"Active" if sensors & self.SEN_AMBIENT else "Inactive"}, Gas: { "Active" if sensors & self.SEN_AIR else "Inactive" }, Humidity: { "Active" if sensors & self.SEN_HUMIDITY else "Inactive" }')
        print(f'\033[KMotor: {motor:x}: Motor: {"Active" if motor & self.MOT_RUNNING else "Inactive"}, Phase: { "Fast" if motor & self.MOT_PHASE_FAST else "Slow" }')
        print(f"\033[KDevice state: {state:x}: Ready: { 'Yes' if (state & self.DEV_STATE_MASK) == self.DEV_STATE_READY else 'No' }, Normal: { 'Yes' if (state & self.DEV_STATE_MASK) == self.DEV_STATE_NORMAL else 'No' }, Forced: { 'Yes' if (state & self.DEV_STATE_MASK) == self.DEV_STATE_FORCED else 'No' }, Local: { 'Yes' if state & self.DEV_STATE_LOCAL else 'No' }, WiFi: { 'Connected' if state & self.DEV_WIFI_CONNECTED else 'Disconnected' }, MQTT: { 'Subscribed' if state & self.DEV_MQTT_SUBSCRIBED else 'Not subscribed' })")

        return 8

# testbench/tbench.py
