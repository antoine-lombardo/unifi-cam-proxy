import os
import ssl
import threading
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import time
import logging
from wss_handler import WSSHandler

latest_session = {}

class VerboseAPIHandler(BaseHTTPRequestHandler):
    logger = logging.getLogger("camera_app")  # Default, can be overridden
    settings = None

    def log_request_info(self, body=None):
        self.logger.info(f"[{self.command}] {self.client_address[0]}:{self.client_address[1]} {self.path}")
        self.logger.debug("Headers:")
        for k, v in self.headers.items():
            self.logger.debug(f"  {k}: {v}")
        if body:
            try:
                self.logger.debug("JSON Body:\n" + json.dumps(json.loads(body), indent=2))
            except Exception:
                self.logger.debug("Raw Body:\n" + body.decode(errors='replace'))

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

                self.settings["connectionHost"] = data.get("mgmt", {}).get("hosts")

                self.logger.info("[*] Stored management session:")
                self.logger.debug(json.dumps(latest_session, indent=2))

            except Exception as e:
                self.logger.error(f"[!] Failed to parse /api/1.2/manage body: {e}")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"result": "success"}).encode())

        if self.settings and self.settings["canAdopt"]:
            self.settings["canAdopt"] = False
            self.logger.info("[*] Updated settings: canAdopt = False")

        now_ms = int(time.time() * 1000)
        self.settings["lastSeen"] = now_ms

        # Uncomment if you want to auto-start WSS after adoption
        """
        handler = WSSHandler(
            token=latest_session["token"],
            host=latest_session["hosts"][0].split(":")[0],
            settings=self.settings,
            verify_cert=False
        )
        threading.Thread(target=handler.run, daemon=True).start()
        """

    def do_PUT(self):
        self.do_POST()

    def do_DELETE(self):
        self.log_request_info()
        self.send_response(204)
        self.end_headers()


class VerboseAPIServer:
    def __init__(self, port=8000, use_ssl=False, certfile="cert.pem", keyfile="key.pem", settings=None, logger=None):
        self.port = port
        self.use_ssl = use_ssl
        self.certfile = certfile
        self.keyfile = keyfile
        self.server = HTTPServer(("0.0.0.0", port), VerboseAPIHandler)
        self.settings = settings

        # Apply shared logger and settings to handler
        VerboseAPIHandler.settings = self.settings
        VerboseAPIHandler.logger = logger or logging.getLogger("camera_app")

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

        VerboseAPIHandler.logger.warning("[!] cert.pem or key.pem not found. Generating self-signed certificate...")

        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:2048",
            "-nodes", "-keyout", self.keyfile, "-out", self.certfile,
            "-days", "365",
            "-subj", "/CN=localhost"
        ], check=True)

        VerboseAPIHandler.logger.info("[+] Self-signed certificate generated.")

    def start(self):
        def _thread():
            protocol = "HTTPS" if self.use_ssl else "HTTP"
            VerboseAPIHandler.logger.info(f"[+] {protocol} API server running on port {self.port}")
            self.server.serve_forever()

        thread = threading.Thread(target=_thread, daemon=True)
        thread.start()
