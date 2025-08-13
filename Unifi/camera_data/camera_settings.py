import json
import os
import sys
import socket
import threading
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from .camera_models import CameraModelDatabase

class CameraSettings:
    def __init__(self, settings_file=None, logger=None):
        self._lock = threading.RLock()
        self.settings_file = settings_file or os.path.join(os.path.dirname(__file__), "settings.json")
        self.settings = {}
        self._dirty = False
        self.logger = logger or logging.getLogger(__name__)

        self._load_or_initialize()
        self._get_ip_address()
        self._get_mac_address()
        self._ensure_platform_and_sysid()
        if self._dirty:
            self._save()

    def _load_or_initialize(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as f:
                self.settings = json.load(f)
            self.logger.info("Loaded existing settings from %s", self.settings_file)
        else:
            self.logger.info("Creating default settings...")
            self.settings = self._default_settings()
            self._save()

    def _ensure_platform_and_sysid(self):
        changed = False
        if not self.settings.get("marketName"):
            model = os.environ.get("CAMERA_MODEL", "").strip()
            if not model:
                self.logger.error("CAMERA_MODEL environment variable is required to set type or platform.")
                sys.exit(1)
            changed |= self._set_nested_value("marketName", model)

        if not self.settings.get("platform"):
            platform = CameraModelDatabase.get_platform(self.settings["marketName"])
            if not platform:
                self.logger.error(f"Unknown platform for type: {self.settings['marketName']}")
                sys.exit(1)
            changed |= self._set_nested_value("platform", platform)

        if not self.settings.get("sysid"):
            sysid = CameraModelDatabase.CameraSysIds.get(self.settings["marketName"])
            if sysid is None:
                self.logger.error(f"Unknown system ID for type: {self.settings['marketName']}")
                sys.exit(1)
            changed |= self._set_nested_value("sysid", sysid)

        if not self.settings.get("type"):
            changed |= self._set_nested_value("type", self.settings["marketName"].replace("_", " "))

        self._dirty |= changed

    def _get_mac_address(self, interface="eth0"):
        if not self.settings.get("mac"):
            try:
                with open(f"/sys/class/net/{interface}/address") as f:
                    mac = f.read().strip()
                    if not mac:
                        self.logger.error(f"Empty MAC address for interface '{interface}'.")
                        sys.exit(1)
                    self._set_nested_value("mac", mac)
            except FileNotFoundError:
                self.logger.error(f"Network interface '{interface}' not found.")
                sys.exit(1)

    def _get_ip_address(self):
        if not self.settings.get("host"):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.connect(("8.8.8.8", 80))
                    ip = s.getsockname()[0]
                    if not ip:
                        self.logger.error("Failed to retrieve IP address.")
                        sys.exit(1)
                    self._set_nested_value("host", ip)
            except Exception as e:
                self.logger.error(f"Failed to get IP address: {e}")
                sys.exit(1)

    def _default_settings(self):
        return {
            "mac": "",                         # MAC address of the device
            "host": "",                        # Hostname or IP address
            "type": "",                        # Device type (e.g., camera, sensor)
            "sysid": "",                       # System hardware identifier
            "platform": "",                    # Platform string (hardware type)
            "marketName": "",                  # Commercial model name
            "canAdopt": True,
            "logging": {
                "level": "INFO",          # a root/fallback level
                "api": { "level": "DEBUG" },
                "discovery": { "level": "INFO" },
                "uptime": { "level": "INFO" },
                "wss": { "level": "DEBUG" }
            }
        }

    def __getitem__(self, key):
        """
        Thread-safe read access to a (possibly nested) setting.
        
        Usage:
            mac = settings["uplinkDevice.mac"]
        """
        with self._lock:
            value = self._get_nested_value(key, default=None)
            if value is None and not self.__contains__(key):
                raise KeyError(key)
            return value

    def __setitem__(self, key, value):
        """
        Thread-safe write access to a (possibly nested) setting. Automatically persists to disk.

        Usage:
            settings["uplinkDevice.mac"] = "00:11:22:33:44:55"
        """
        with self._lock:
            if self._set_nested_value(key, value):
                self._save()

    def __contains__(self, key):
        """
        Thread-safe key existence check for nested keys.

        Usage:
            if "uplinkDevice.mac" in settings:
                ...
        """
        with self._lock:
            return self._get_nested_value(key, default=None) is not None

    def get(self, key, default=None):
        """
        Thread-safe retrieval with fallback for nested keys.

        Usage:
            mac = settings.get("uplinkDevice.mac", "00:00:00:00:00:00")
        """
        with self._lock:
            return self._get_nested_value(key, default)

    def update(self, updates: dict):
        """
        Thread-safe bulk update (flat keys only).
        Automatically persists to disk.

        Usage:
            settings.update({
                "firmwareVersion": "v5.0.0",
                "isUpdating": False
            })
        """
        with self._lock:
            changed = False
            for k, v in updates.items():
                changed |= self._set_nested_value(k, v)
            if changed:
                self._save()

    def _get_nested_value(self, dotted_key, default=None):
        """Internal helper to retrieve nested values using dot-notation."""
        keys = dotted_key.split(".")
        value = self.settings
        for key in keys:
            if not isinstance(value, dict) or key not in value:
                return default
            value = value[key]
        return value

    def _save(self):
        with self._lock:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=4)

    def _set_nested_value(self, dotted_key, value, overwrite_non_dict=False) -> bool:
        """Set nested value using dot-notation. Return True if it changed."""
        keys = dotted_key.split(".")
        d = self.settings
        for key in keys[:-1]:
            cur = d.get(key)
            if cur is None:
                cur = {}
                d[key] = cur
            elif not isinstance(cur, dict):
                if not overwrite_non_dict:
                    raise TypeError(f"Cannot descend into non-dict at '{key}' for '{dotted_key}'")
                cur = {}
                d[key] = cur
            d = cur
        last = keys[-1]
        if last in d and d[last] == value:
            return False
        d[last] = value
        self._dirty = True
        return True

    def mac_bytes(self, key="mac"):
        """
        Returns the MAC address (from key path) as raw bytes.
        Returns None if value is missing or malformed.

        Usage:
            settings.mac_bytes("mac")
            settings.mac_bytes("uplinkDevice.mac")
        """
        with self._lock:
            mac_str = self._get_nested_value(key)
        if not mac_str:
            raise RuntimeError("MAC address is missing in settings.")
        try:
            return bytes.fromhex(mac_str.replace(":", ""))
        except ValueError:
            raise RuntimeError(f"Malformed MAC address: {mac_str!r}")

    def ip_bytes(self, key="host"):
        """
        Returns the IP address (from key path) as raw bytes.
        Returns None if value is missing or malformed.

        Usage:
            settings.ip_bytes("host")
            settings.ip_bytes("wifiConnectionState.apMgmtIp")
        """
        with self._lock:
            ip_str = self._get_nested_value(key)
        if not ip_str:
            raise RuntimeError("IP address is missing in settings.")
        try:
            return socket.inet_aton(ip_str)
        except OSError:
            raise RuntimeError(f"Malformed IP address: {ip_str!r}")