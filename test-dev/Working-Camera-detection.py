"""
This script simulates a UniFi-compatible camera for discovery testing.

✔️ Camera is detected by UniFi Protect and can be "added" (but not adopted).
"""

import socket
import struct
import threading
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

# ---- Config ----
DISCOVERY_PORT = 10001
FAKE_CAMERA_IP = "192.168.1.X"  # Replace with a LAN IP on your subnet

# UniFi Protect discovery protocol constants
VERSION = 1
CMD_INFO = 0

# Camera identity (replace values as needed)
PLATFORM = "s5l"
MODEL = "UVC G4 Bullet"
MODEL_SHORT = "G4 Bullet"
SYSTEM_ID = 0xa572  # Little-endian camera type ID
GUID = bytes.fromhex("a1b2c3d4e5f60718293a4b5c6d7e8f90") #replace this with a new random GUID.
CONTROLLER_ID = bytes.fromhex("99887766554433221100ffeeddccbbaa")  # Dummy UUID

# Fake network identity
MAC = bytes.fromhex("112233445566")
IP = socket.inet_aton("192.168.1.X")  # Replace with same IP as FAKE_CAMERA_IP
PRIMARY_ADDRESS = MAC + IP

def build_field(field_id, data):
    return struct.pack(">BH", field_id, len(data)) + data

def build_discovery_response():
    payload = b""
    payload += build_field(1, MAC)                                      # HWADDR
    payload += build_field(11, b"FakeCam")                              # HOSTNAME
    payload += build_field(12, PLATFORM.encode())                       # PLATFORM
    payload += build_field(14, struct.pack("B", 1))                     # WMODE (1 = Wired)
    payload += build_field(13, b"TestSSID")                             # ESSID
    payload += build_field(3, b"5.0.129")                               # FWVERSION
    payload += build_field(32, b"24:a4:3c:7b:92:11")                    # DEVICE_ID
    payload += build_field(10, struct.pack(">I", int(time.time())))     # UPTIME
    payload += build_field(15, struct.pack(">HH", 0, 443))              # WEBUI (HTTPS + port)
    payload += build_field(16, struct.pack("<H", SYSTEM_ID))            # SYSTEM_ID (LE)
    payload += build_field(20, MODEL.encode())                          # MODEL
    payload += build_field(21, MODEL_SHORT.encode())                    # MODEL_SHORT
    payload += build_field(47, PRIMARY_ADDRESS)                         # PRIMARY_ADDRESS
    payload += build_field(44, struct.pack("B", 1))                     # DEVICE_DEFAULT_CREDENTIALS
    payload += build_field(43, GUID)                                    # GUID
    payload += build_field(38, CONTROLLER_ID)                           # CONTROLLER_ID

    header = struct.pack(">BBH", VERSION, CMD_INFO, len(payload))
    return header + payload

def start_fake_camera():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((FAKE_CAMERA_IP, DISCOVERY_PORT))

    print(f"[*] Listening for discovery on {FAKE_CAMERA_IP}:{DISCOVERY_PORT}")

    while True:
        data, addr = sock.recvfrom(1024)
        print(f"[>] Received discovery from {addr}\n    Raw: {data.hex()}")

        if data[:4] == b"\x01\x00\x00\x00":
            response = build_discovery_response()
            print("[<] Sending discovery response:\n    " + response.hex())
            sock.sendto(response, addr)

# ---- HTTPS/HTTP API Logging Server ----
class VerboseAPIHandler(BaseHTTPRequestHandler):
    def log_request_info(self):
        print("\n" + "="*60)
        print(f"[{self.command}] {self.client_address[0]}:{self.client_address[1]} {self.path}")
        print("Headers:")
        for k, v in self.headers.items():
            print(f"  {k}: {v}")
        if self.command in ["POST", "PUT"]:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                print("JSON Body:")
                print(json.dumps(json.loads(body), indent=2))
            except:
                print("Raw Body:")
                print(body.decode(errors='replace'))

    def do_GET(self):
        self.log_request_info()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_POST(self):
        self.log_request_info()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

    def do_PUT(self): self.do_POST()
    def do_DELETE(self):
        self.log_request_info()
        self.send_response(204)
        self.end_headers()

def run_http_server(port):
    def _thread():
        server = HTTPServer(("0.0.0.0", port), VerboseAPIHandler)
        print(f"[+] HTTP API server running on port {port}")
        server.serve_forever()
    threading.Thread(target=_thread, daemon=True).start()

# ---- Main Entrypoint ----
if __name__ == "__main__":
    start_fake_camera()

    # Start HTTP/HTTPS servers for adoption testing
    run_http_server(80)

    # Prevent script from exiting
    threading.Event().wait()
