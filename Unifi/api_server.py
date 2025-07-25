import os
import ssl
import threading
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from camera_data.camera_settings import CameraSettings
from wss_handler import WSSHandler
import json
import time

latest_session = {}

class VerboseAPIHandler(BaseHTTPRequestHandler):
    def log_request_info(self, body=None):
        print("\n" + "=" * 60)
        print(f"[{self.command}] {self.client_address[0]}:{self.client_address[1]} {self.path}")
        print("Headers:")
        for k, v in self.headers.items():
            print(f"  {k}: {v}")
        if body:
            try:
                print("JSON Body:")
                print(json.dumps(json.loads(body), indent=2))
            except Exception:
                print("Raw Body:")
                print(body.decode(errors='replace'))

    def do_GET(self):
        self.log_request_info()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        self.log_request_info(body)

        if self.path == "/api/1.2/manage":
            try:
                data = json.loads(body)

                latest_session["token"] = data.get("mgmt", {}).get("token")
                latest_session["hosts"] = data.get("mgmt", {}).get("hosts")
                latest_session["protocol"] = data.get("mgmt", {}).get("protocol")
                latest_session["consoleId"] = data.get("mgmt", {}).get("consoleId")
                latest_session["raw"] = data

                print("[*] Stored management session:")
                print(json.dumps(latest_session, indent=2))

            except Exception as e:
                print(f"[!] Failed to parse /api/1.2/manage body: {e}")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"result": "success"}).encode())

        if self.settings and self.settings["canAdopt"]:
            self.settings["canAdopt"] = False
            print("[*] Updated settings: canAdopt = False")
        now_ms = int(time.time() * 1000)
        self.settings["lastSeen"] = now_ms
    '''
        handler = WSSHandler(
            token=latest_session["token"],
            host=latest_session["hosts"][0].split(":")[0],
            settings=self.settings,
            verify_cert=False
        )
        threading.Thread(target=handler.run, daemon=True).start()
    '''
    def do_PUT(self):
        self.do_POST()

    def do_DELETE(self):
        self.log_request_info()
        self.send_response(204)
        self.end_headers()


class VerboseAPIServer:
    def __init__(self, port=8000, use_ssl=False, certfile="cert.pem", keyfile="key.pem", settings=None):
        self.port = port
        self.use_ssl = use_ssl
        self.certfile = certfile
        self.keyfile = keyfile
        self.server = HTTPServer(("0.0.0.0", port), VerboseAPIHandler)
        self.settings = settings

        VerboseAPIHandler.settings = self.settings

        if self.use_ssl:
            self._ensure_cert_exists()
            self.server.socket = ssl.wrap_socket(
                self.server.socket,
                keyfile=self.keyfile,
                certfile=self.certfile,
                server_side=True
            )

    def _ensure_cert_exists(self):
        if os.path.exists(self.certfile) and os.path.exists(self.keyfile):
            return

        print("[!] cert.pem or key.pem not found. Generating self-signed certificate...")

        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:2048",
            "-nodes", "-keyout", self.keyfile, "-out", self.certfile,
            "-days", "365",
            "-subj", "/CN=localhost"
        ], check=True)

        print("[+] Self-signed certificate generated.")

    def start(self):
        def _thread():
            protocol = "HTTPS" if self.use_ssl else "HTTP"
            print(f"[+] {protocol} API server running on port {self.port}")
            self.server.serve_forever()

        thread = threading.Thread(target=_thread, daemon=True)
        thread.start()
