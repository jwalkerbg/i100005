# ms_host.py

import struct
from  mqttms import MSProtocol
from smartfan.logger import get_app_logger

logger = get_app_logger(__name__)

class MShost:
    def __init__(self, ms_protocol: MSProtocol, config):
        self.ms_protocol = ms_protocol
        self.config = config

    def ms_simple_command(self, cmd: str):
        payload = f'{{"command":"{cmd}","data":""}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_command_send_uint16(self, cmd: str, value: int):
        format_string = '<H'
        pd = struct.pack(format_string,value).hex()
        payload = f'{{"command":"{cmd}","data":"{pd}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_command_send_uint8(self, cmd: str, value: int):
        format_string = '<B'
        pd = struct.pack(format_string,value).hex()
        payload = f'{{"command":"{cmd}","data":"{pd}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_who_am_i(self):
        return self.ms_simple_command("WH")

    def ms_nop(self):
        return self.ms_simple_command("NP")

    def ms_sensors(self):
        return self.ms_simple_command("SR")

    def ms_wificred(self, ssid: str, password: str):
        ssid_bytes = ssid.encode('ascii')
        password_bytes = password.encode('ascii')
        data = bytearray(ssid_bytes) + b'\0' + bytearray(password_bytes)
        data = data.hex()
        payload = f'{{"command":"WF","data":"{data}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_set_mode(self, mode: int):
        format_string = 'B'
        pd = struct.pack(format_string,mode).hex()
        payload = f'{{"command":"MD","data":"{pd}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_getsmac(self):
        return self.ms_simple_command("GM")

    def ms_set_amb_thr(self, value: int):
        return self.ms_command_send_uint16("AH", value)

    def ms_set_hum_thr(self, value: int):
        return self.ms_command_send_uint16("HH", value)

    def ms_set_gas_thr(self, value: int):
        return self.ms_command_send_uint16("GH", value)

    def ms_set_forced_time(self, value: int):
        return self.ms_command_send_uint16("FT", value)

    def ms_set_post_time(self, value: int):
        return self.ms_command_send_uint16("PT", value)

    def ms_ambient_light(self, value: int):
        return self.ms_command_send_uint16("AL", value)

    def ms_get_params(self):
        return self.ms_simple_command("PG")

    def ms_start_vent(self):
        return self.ms_simple_command("SV")

    def ms_logs(self, value: int):
        return self.ms_command_send_uint16("PT", value)

    def ms_mqtt_ready(self):
        return self.ms_simple_command("MQ")

    def ms_restart(self):
        return self.ms_simple_command("RS")

    def ms_version(self):
        return self.ms_simple_command("VS")

    def ms_serial(self, sn: str):
        sn_bytes = sn.encode('ascii')
        data = sn_bytes.hex()
        payload = f'{{"command":"SN","data":"{data}"}}'
        self.ms_protocol.put_command(payload)

        self.ms_protocol.response_received.wait()
        payload = self.ms_protocol.response
        logger.info(f"MSH response: {payload}")
        self.ms_protocol.response_received.clear()
        return payload

    def ms_getmachid(self):
        return self.ms_simple_command("ZA")

    def ms_motor(self, mode:int):
        return self.ms_command_send_uint8("MT",mode)

    def ms_testmode(self):
        return self.ms_simple_command("TM")

    def ms_led(self, mode:int):
        return self.ms_command_send_uint8("LE",mode)
