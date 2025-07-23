import socket
import struct
import time


class DiscoveryResponder:
    DISCOVERY_PORT = 10001
    VERSION = 1
    CMD_INFO = 0

    def __init__(self, settings):
        self.settings = settings
        self.primary_address = self.settings.mac_bytes + self.settings.ip_bytes

    def build_field(self, field_id, data):
        return struct.pack(">BH", field_id, len(data)) + data


    def build_response(self):
        payload = b""
        payload += self.build_field(1,  self.settings.mac_bytes)                        # HWADDR
        payload += self.build_field(11, self.settings.get("host").encode())             # HOSTNAME
        payload += self.build_field(12, self.settings.get("platform").encode())         # PLATFORM
        payload += self.build_field(14, struct.pack("B", 1))                            # WMODE
        payload += self.build_field(13, b"")                                            # ESSID
        payload += self.build_field(3, b"5.0.129")                                      # FWVERSION
        payload += self.build_field(32, self.settings.get("mac").encode())              # DEVICE_ID (string MAC)
        payload += self.build_field(10, struct.pack(">I", int(time.time())))            # UPTIME
        payload += self.build_field(15, struct.pack(">HH", 0, 443))                     # WEBUI (https)
        payload += self.build_field(16, struct.pack("<H", self.settings.get("sysid")))  # SYSTEM_ID (LE)
        payload += self.build_field(20, self.settings.get("type").encode())             # MODEL
        payload += self.build_field(21, self.settings.get("type").replace("UVC_", "").replace("_", " ").encode()) # MODEL_SHORT
        payload += self.build_field(47, self.primary_address)                           # PRIMARY_ADDRESS (MAC + IP)
        payload += self.build_field(44, struct.pack("B", 1))                            # DEVICE_DEFAULT_CREDENTIALS
        payload += self.build_field(43, b"")                                            # GUID
        payload += self.build_field(38, b"")                                            # CONTROLLER_ID

        header = struct.pack(">BBH", self.VERSION, self.CMD_INFO, len(payload))
        return header + payload

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", self.DISCOVERY_PORT))

        print(f"[*] Listening for discovery on {self.settings.get('host')}:{self.DISCOVERY_PORT}")

        while True:
            data, addr = sock.recvfrom(1024)
            print(f"[>] Received discovery from {addr}\n    Raw: {data.hex()}")

            if data[:4] == b"\x01\x00\x00\x00":
                response = self.build_response()
                print("[<] Sending discovery response:\n    " + response.hex())
                sock.sendto(response, addr)
