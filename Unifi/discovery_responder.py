import socket
import struct
import logging


class DiscoveryResponder:
    DISCOVERY_PORT = 10001
    VERSION = 1
    CMD_INFO = 0

    def __init__(self, settings, logger=None):
        self.settings = settings
        self.log = logger or logging.getLogger("camera_app")
        self.primary_address = self.settings.mac_bytes("mac") + self.settings.ip_bytes("host")

    def build_field(self, field_id, data):
        return struct.pack(">BH", field_id, len(data)) + data

    def build_response(self):
        payload = b""

        payload += self.build_field(1, self.settings.mac_bytes("mac"))                     # HWADDR
        payload += self.build_field(11, self.settings["host"].encode())                    # HOSTNAME
        payload += self.build_field(12, self.settings["platform"].encode())                # PLATFORM
        payload += self.build_field(14, struct.pack("B", 1))                               # WMODE (1 = wired)
        payload += self.build_field(13, b"")                                               # ESSID
        payload += self.build_field(3, self.settings["firmwareVersion"].encode())          # FWVERSION
        payload += self.build_field(32, self.settings["mac"].encode())                     # DEVICE_ID
        payload += self.build_field(10, struct.pack(">I", self.settings["uptime"]))        # UPTIME

        # WEBUI: protocol (1 for https) and port (443)
        webui = struct.pack(">HH", 0, 80)
        payload += self.build_field(15, webui)

        # SYSTEM_ID: 2 bytes little endian
        sysid_le = struct.pack("<H", self.settings["sysid"])
        payload += self.build_field(16, sysid_le)

        # DEVICE_DEFAULT_CREDENTIALS
        payload += self.build_field(44, struct.pack("B", 1))

        # GUID (optional, must be 16 bytes)
        guid = self.settings.get("guid")
        if guid:
            payload += self.build_field(43, bytes.fromhex(guid.replace("-", "")))

        # CONTROLLER_ID (optional, 16 bytes UUID)
        controller_id = self.settings.get("controllerId")
        if controller_id:
            payload += self.build_field(38, bytes.fromhex(controller_id.replace("-", "")))

        # PRIMARY_ADDRESS: MAC (6 bytes) + IP (4 bytes)
        payload += self.build_field(47, self.primary_address)

        # Header
        header = struct.pack(">BBH", self.VERSION, self.CMD_INFO, len(payload))
        return header + payload

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", self.DISCOVERY_PORT))

        self.log.info(f"Listening for discovery on {self.settings['host']}:{self.DISCOVERY_PORT}")

        while True:
            if not self.settings["canAdopt"]:
                self.log.warning("Exiting discovery loop because canAdopt is False.")
                break

            sock.settimeout(1.0)
            try:
                data, addr = sock.recvfrom(1024)
            except socket.timeout:
                continue

            self.log.debug(f"Received discovery from {addr} | Raw: {data.hex()}")

            if data[:4] == b"\x01\x00\x00\x00":
                response = self.build_response()
                self.log.debug(f"Sending discovery response: {response.hex()}")
                sock.sendto(response, addr)
