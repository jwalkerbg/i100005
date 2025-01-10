# testbench/tbench.py

from smartfan.logger import getAppLogger

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

    def tests(self):
        pass



