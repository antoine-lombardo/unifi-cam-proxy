import asyncio
import websockets
import ssl
import json
import socket
import traceback
import uuid
import time
from datetime import datetime, timezone

class WSSHandler:
    def __init__(self, token, host, settings, verify_cert=False, logger=None):
        self.token = token
        self.host = host
        self.settings = settings  # Expected keys: mac, type, platform, firmwareVersion, hardwareRevision, name
        self.verify_cert = verify_cert
        self.logger = logger  # Shared logger instance (e.g., from main.py)

    def format_mac(self, mac: str) -> str:
        return mac.replace(":", "").upper()

    def format_colon_mac(self, mac: str) -> str:
        return ':'.join(mac[i:i+2] for i in range(0, len(mac), 2)).lower()

    def format_camera_model(self, model: str) -> str:
        return model.replace("_", "-").upper()

    def get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((self.host, 1))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def generate_hello_payload(self, raw_mac):
        now_ms = int(time.time() * 1000)
        iso_ts = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

        return {
            "functionName": "ubnt_avclient_hello",
            "messageId": str(uuid.uuid4()),
            "payload": {
                "mac": self.format_colon_mac(raw_mac),
                "model": self.format_camera_model(self.settings["type"]),
                "firmwareVersion": self.settings.get("firmwareVersion", "v4.63.11"),
                "hardwareRevision": self.settings.get("hardwareRevision", "rev1"),
                "platform": self.settings.get("platform", "ambarella"),
                "uptime": 10,
                "connectedSince": now_ms,
                "lastSeen": now_ms,
                "state": "CONNECTED"
            },
            "timeStamp": iso_ts
        }

    async def connect(self):
        uri = f"wss://{self.host}:7442/camera/1.0/ws?token={self.token}"
        ssl_context = ssl.create_default_context()

        if not self.verify_cert:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        raw_mac = self.format_mac(self.settings["mac"])
        colon_mac = self.format_colon_mac(raw_mac)
        ip = self.get_local_ip()

        headers = {
            "Origin": f"https://{self.host}",
            "Host": f"{self.host}:7442",
            "camera-mac": colon_mac,
            "x-ident": raw_mac,
            "camera-model": self.settings["type"],
            "x-type": "camera",
            "x-token": self.token,
            "x-ip": ip,
            "x-fw-version": self.settings["firmwareVersion"],
            "x-hw-rev": self.settings["hardwareRevision"],
            "x-camera-name": self.settings["name"],
            "x-platform": self.settings["platform"],
            "User-Agent": "node/v12.22.1",
            "Sec-WebSocket-Protocol": "secure_transfer"
        }

        self.logger.info(f"[+] Connecting to {uri}")
        self.logger.debug(f"[+] Using headers: {headers}")

        try:
            async with websockets.connect(
                uri,
                ssl=ssl_context,
                origin=headers["Origin"],
                subprotocols=["secure_transfer"],
                additional_headers=headers,
                open_timeout=10,
                ping_interval=20,
                ping_timeout=20,
                close_timeout=10
            ) as ws:
                self.logger.info("[+] Connected to UniFi Protect")

                hello_msg = self.generate_hello_payload(raw_mac)
                self.logger.debug("[>] Sending hello payload: %s", hello_msg)
                await ws.send(json.dumps(hello_msg))
                self.logger.info("[>] Sent ubnt_avclient_hello")

                while True:
                    message = await ws.recv()
                    self.logger.debug("[<] Raw message: %r", message)
                    try:
                        parsed = json.loads(message)
                        msg_type = parsed.get("functionName", "unknown")
                        self.logger.info(f"[<] Type: {msg_type} | Message: {parsed}")
                    except json.JSONDecodeError:
                        self.logger.warning("[!] Received non-JSON message: %s", message)

        except Exception as e:
            self.logger.error("[!] WebSocket connection failed: %s", e)
            self.logger.debug(traceback.format_exc())

    def run(self):
        asyncio.run(self.connect())
