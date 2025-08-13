import asyncio
import contextlib
import json
import logging
import os
import ssl
import time
import threading
from datetime import datetime, timezone
from typing import Optional, Tuple
import websockets  # type: ignore
from websockets.client import WebSocketClientProtocol  # type: ignore



def _now_iso() -> str:
    """UTC ISO8601 with timezone (Z)."""
    return datetime.now(timezone.utc).isoformat()


def _parse_hostport(hostport: str) -> Tuple[str, int]:
    """Parse 'host:port' safely (last colon split for IPv6-with-port cases)."""
    if ":" in hostport:
        host, port_s = hostport.rsplit(":", 1)
        try:
            return host, int(port_s)
        except ValueError:
            return host, 7442
    return hostport, 7442


class WssManager(threading.Thread):
    """
    Watches settings for mgmt.token + mgmt.connectionHost and maintains
    a WSS connection to the controller. Replies to the minimal set of
    messages the controller sends during pairing/idle.

    Expects:
      settings["mgmt.token"] (str)
      settings["mgmt.connectionHost"] (e.g., "192.168.0.1:7442")
      settings["mac"], settings["host"], settings["firmwareVersion"], settings["sysid"]
    """

    # Toggle this if your controller build misbehaves with subprotocol header.
    USE_SECURE_TRANSFER_SUBPROTOCOL = True

    def __init__(
        self,
        settings,
        token_event: threading.Event,
        stop_event: threading.Event,
        logger: logging.Logger,
    ):
        super().__init__(daemon=True, name="WSSManager")
        self.settings = settings
        self.token_event = token_event
        self.stop_event = stop_event
        self.log = logger

        self._msg_id = 0

    # -------------------- public thread API --------------------

    def run(self):
        current_key: Optional[Tuple[str, int, str]] = None

        while not self.stop_event.is_set():
            token = self.settings.get("mgmt.token")
            hostport = self.settings.get("mgmt.connectionHost")

            if not token or not hostport:
                self.log.debug("WSS: waiting for token/host...")
                # sleep or wait for token_event
                self.token_event.wait(timeout=10)
                self.token_event.clear()
                continue

            host, port = _parse_hostport(str(hostport))
            key = (host, port, token)

            # reconnect if any part changed
            if key != current_key:
                self.log.info(
                    "WSS: (re)connecting to %s:%s (token/host changed)", host, port
                )
                current_key = key

            # Run one connect-serve attempt (async) — reconnect on error/close
            try:
                asyncio.run(self._connect_and_serve(host, port, token))
            except Exception as e:
                self.log.warning("WSS: connection failed: %s; retrying in 5s", e)
                # Brief delay or sooner if token rotates
                self.token_event.wait(timeout=5)
                self.token_event.clear()

    # -------------------- async client --------------------

    async def _connect_and_serve(self, host: str, port: int, token: str):
        url = f"wss://{host}:{port}/camera/1.0/ws?token={token}"

        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        # Controller uses self-signed cert — skip validation unless you have CA
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE

        # Present our cert/key if available (matches your HTTPS keypair)
        certfile = "cert.pem"
        keyfile = "key.pem"
        if os.path.exists(certfile) and os.path.exists(keyfile):
            try:
                ssl_ctx.load_cert_chain(certfile=certfile, keyfile=keyfile)
            except Exception as e:
                self.log.warning("WSS: could not load client cert/key: %s", e)

        headers = {
            "Camera-Mac": (self.settings["mac"] or "").lower(),
            # Controller often expects hex sysid string here (e.g. "0xa573")
            "Camera-Model": self.settings.get("sysid", "") or "",
        }

        kwargs = dict(
            ssl=ssl_ctx,
            additional_headers=headers,
        )
        if self.USE_SECURE_TRANSFER_SUBPROTOCOL:
            kwargs["subprotocols"] = ["secure_transfer"]

        self.log.info("WSS: connecting to controller")
        self.log.debug(
            "WSS: URL=%s subprotocols=%s headers=%s",
            url,
            kwargs.get("subprotocols"),
            headers,
        )

        try:
            async with websockets.connect(url, **kwargs) as ws:
                self.log.info("WSS: connected to controller")
                await self._serve_loop(ws)
        except websockets.exceptions.InvalidHandshake as e:
            # Retry once without subprotocol if handshake fails
            if self.USE_SECURE_TRANSFER_SUBPROTOCOL:
                self.log.warning(
                    "WSS: handshake failed with subprotocol; retrying without. Error: %s",
                    e,
                )
                await asyncio.sleep(1)
                async with websockets.connect(url, ssl=ssl_ctx, additional_headers=headers) as ws:
                    self.log.info("WSS: connected to controller (no subprotocol)")
                    await self._serve_loop(ws)
            else:
                raise
        except websockets.exceptions.ConnectionClosedError as e:
            self.log.error("WSS: closed: code=%s reason=%s", e.code, e.reason)
            raise
        except Exception:
            # Bubble up; run() handles retry/backoff
            raise

    async def _serve_loop(self, ws: WebSocketClientProtocol):
        # Send hello first
        await self._send_hello(ws)

        # Optional: start periodic “stats” pings (lightweight)
        stats_task = asyncio.create_task(self._periodic_stats(ws))

        try:
            async for incoming in ws:
                # binary frames — just log and ignore for now
                if isinstance(incoming, (bytes, bytearray)):
                    self.log.debug("WSS <- (binary %d bytes)", len(incoming))
                    continue

                # text frames (expected JSON)
                try:
                    msg = json.loads(incoming)
                except json.JSONDecodeError:
                    self.log.debug("WSS <- (non-JSON text, len=%d)", len(incoming))
                    continue

                self.log.debug("WSS <- %s", json.dumps(msg, indent=2))

                fn = msg.get("functionName")
                mid = msg.get("messageId", 0)
                expect = bool(msg.get("responseExpected"))

                # No reply if not requested (except for initial handshake acks we explicitly handle)
                if not expect and fn not in ("ubnt_avclient_hello",):
                    self.log.debug("WSS: controller did not request response for %s; skipping ACK", fn)
                    continue

                # Handle specific functions
                if fn == "ubnt_avclient_paramAgreement":
                    await self._send_ok(ws, fn, mid)
                    continue

                if fn in ("ubnt_avclient_timeSync", "ubnt_avclient_configure", "ubnt_avclient_start"):
                    await self._send_ok(ws, fn, mid)
                    continue

                if fn == "ChangeVideoSettings":
                    payload_in = msg.get("payload") or {}
                    await self._send(ws, fn, mid, {
                        "statusCode": 0,
                        "status": "ok",
                        "videoSettings": payload_in,  # echo back
                    })
                    continue

                if fn == "ChangeIspSettings":
                    payload_in = msg.get("payload") or {}
                    await self._send(ws, fn, mid, {
                        "statusCode": 0,
                        "status": "ok",
                        "ispSettings": payload_in,  # echo back
                    })
                    continue

                if fn == "NetworkStatus":
                    await self._send(ws, fn, mid, {
                        "statusCode": 0,
                        "status": "connected",
                        "ip": self.settings["host"],
                        "mac": (self.settings["mac"] or "").lower(),
                    })
                    continue

                if fn == "GetSystemStats":
                    await self._send(ws, fn, mid, {
                        "statusCode": 0,
                        "cpu": 5,
                        "memory": 20,
                        "temperature": 45,
                        "uptime": self.settings.get("uptime", 0) or 0,
                    })
                    continue

                # Default OK for anything else that expects a response
                if expect:
                    await self._send_ok(ws, fn, mid)

        finally:
            with contextlib.suppress(Exception):
                stats_task.cancel()
                await stats_task

    # -------------------- message builders --------------------

    def _next_msg_id(self) -> int:
        self._msg_id += 1
        return self._msg_id

    async def _send_hello(self, ws: WebSocketClientProtocol):
        hello = {
            "functionName": "ubnt_avclient_hello",
            "messageId": self._next_msg_id(),
            "timeStamp": _now_iso(),
            "payload": {
                "deviceID": (self.settings["mac"] or "").upper(),
                "fwVersion": self.settings.get("firmwareVersion", "v5.0.129"),
                "ip": self.settings["host"],
                "uptime": self.settings.get("uptime", 0) or 0,
                "connectionHost": self.settings["host"],
                "connectionSecurePort": 7442,
                "protocolVersion": 1,
            },
        }
        s = json.dumps(hello, separators=(",", ":"))
        self.log.debug("WSS -> ubnt_avclient_hello: %s", s)
        await ws.send(s)

    async def _send_ok(self, ws: WebSocketClientProtocol, in_fn: str, in_msg_id: int):
        await self._send(ws, in_fn, in_msg_id, {"statusCode": 0, "status": "ok"})

    async def _send(self, ws: WebSocketClientProtocol, in_fn: str, in_msg_id: int, payload_obj: dict):
        out = {
            "from": "ubnt_avclient",
            "to": "UniFiVideo",
            "functionName": in_fn,
            "messageId": self._next_msg_id(),
            "inResponseTo": in_msg_id,
            "timeStamp": _now_iso(),
            "payload": {
                "deviceID": (self.settings["mac"] or "").upper(),
                **payload_obj,
            },
        }
        s = json.dumps(out, separators=(",", ":"))
        self.log.debug("WSS -> %s: %s", in_fn, s)
        await ws.send(s)

    # -------------------- periodic tasks --------------------

    async def _periodic_stats(self, ws: WebSocketClientProtocol):
        """
        Very light periodic update—purely to keep some controllers happy.
        Safe to remove if not needed.
        """
        while True:
            await asyncio.sleep(10)
            try:
                payload = {
                    "type": "cameras.syncStatsAndVideo",
                    "timeStamp": _now_iso(),
                    "payload": {
                        "mac": self.settings["mac"],
                        "stats": {"uptime": self.settings.get("uptime", 0) or 0},
                    },
                }
                s = json.dumps(payload, separators=(",", ":"))
                self.log.debug("WSS -> cameras.syncStatsAndVideo: %s", s)
                await ws.send(s)
            except Exception as e:
                self.log.debug("WSS: periodic stats send failed: %s", e)
                return
