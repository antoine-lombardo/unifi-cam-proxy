import json
import os
import sys
import socket
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from .camera_models import CameraModelDatabase

class CameraSettings:
    def __init__(self, settings_file=None):
        self._lock = threading.RLock()
        self.settings_file = settings_file or os.path.join(os.path.dirname(__file__), "settings.json")
        self.settings = {}

        self._load_or_initialize()
        self._ensure_mac_and_ip()
        self._set_type_and_platform_from_env()
        self._ensure_platform_and_sysid()
        self._save()

    def _load_or_initialize(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as f:
                self.settings = json.load(f)
            print("[=] Loaded existing settings.")
        else:
            print("[*] Creating default settings...")
            self.settings = self._default_settings()

    def _ensure_mac_and_ip(self):
        if not self.settings.get("mac"):
            mac = self._get_mac_address()
            if mac:
                self.settings["mac"] = mac
                print(f"[+] MAC address set: {mac}")
            else:
                print("[!] Failed to get MAC address.")
                exit(1)

        if not self.settings.get("host"):
            ip = self._get_ip_address()
            if ip:
                self.settings["host"] = ip
                print(f"[+] IP address set: {ip}")
            else:
                print("[!] Failed to get IP address.")
                exit(1)
    
    def _ensure_platform_and_sysid(self):
        camera_type = self.settings.get("type")

        if not camera_type:
            print("[!] Camera type not set in settings.")
            exit(1)

        if not self.settings.get("platform"):
            platform = CameraModelDatabase.get_platform(camera_type)
            if platform:
                self.settings["platform"] = platform
                print(f"[+] Platform set: {platform}")
            else:
                print(f"[!] Unknown platform for type: {camera_type}")
                exit(1)

        if not self.settings.get("sysid"):
            sysid = CameraModelDatabase.CameraSysIds.get(camera_type)
            if sysid:
                self.settings["sysid"] = sysid
                print(f"[+] System ID set: 0x{sysid:04x}")
            else:
                print(f"[!] Unknown system ID for type: {camera_type}")
                exit(1)

    def _get_mac_address(self, interface="eth0"):
        try:
            with open(f"/sys/class/net/{interface}/address") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None

    def _get_ip_address(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return None

    def _set_type_and_platform_from_env(self):
        env_type = os.environ.get("CAMERA_TYPE", "").strip()

        # Exit early if type or platform is missing and we can't proceed
        if not self.settings.get("type") or not self.settings.get("platform"):
            if not env_type:
                print("[!] CAMERA_TYPE environment variable is required to set type or platform.")
                exit(1)

            # Set type if missing
            if not self.settings.get("type"):
                self.settings["type"] = env_type
                print(f"[+] Set camera type: {env_type}")

            # Set platform if missing
            if not self.settings.get("platform"):
                platform = CameraModelDatabase.get_platform(env_type)
                if platform:
                    self.settings["platform"] = platform
                    print(f"[+] Set camera platform: {platform}")
                else:
                    print(f"[!] Unknown platform for camera type: {env_type}")
                    exit(1)
    
    def _default_settings(self):
        return {
            "isDeleting": False,               # Flag indicating the device is being deleted
            "mac": "",                         # MAC address of the device
            "host": "",                        # Hostname or IP address
            "connectionHost": "",              # Direct connection host (used for peer connections)
            "type": "",                        # Device type (e.g., camera, sensor)
            "sysid": "",                       # System hardware identifier
            "name": "",                        # Friendly display name
            "upSince": 0,                      # Timestamp when the device last started
            "uptime": 0,                       # Uptime in seconds
            "lastSeen": 0,                     # Last time the device was seen by the controller
            "connectedSince": 0,               # Timestamp since when the device has been connected
            "state": "CONNECTED",              # Connection state (e.g., CONNECTED, DISCONNECTED)
            "lastDisconnect": 0,               # Timestamp of last disconnection
            "hardwareRevision": "",            # Hardware revision string
            "firmwareVersion": "",             # Current firmware version
            "latestFirmwareVersion": "",       # Latest available firmware version
            "latestFirmwareSizeBytes": 0,      # Size of the latest firmware image
            "firmwareBuild": "",               # Internal firmware build identifier
            "isUpdating": False,               # Indicates a firmware update is in progress
            "isDownloadingFW": False,          # Indicates firmware is currently being downloaded
            "fwUpdateState": "upToDate",       # Firmware update status
            "isAdopting": False,               # True if the device is in the adoption process
            "isRestoring": False,              # True if the device is restoring from backup
            "isAdopted": True,                 # True if the device is adopted by the controller
            "isAdoptedByOther": False,         # True if the device is adopted by another controller
            "isProvisioned": True,             # True if the device has completed provisioning
            "isRebooting": False,              # True if the device is rebooting
            "isSshEnabled": False,             # SSH enabled status
            "canAdopt": True,                 # Whether the controller is able to adopt the device
            "isAttemptingToConnect": False,    # True if device is trying to connect to controller
            "uplinkDevice": {                  # Info about the upstream switch or AP
                "name": "",                    # Uplink device name
                "mac": "",                     # MAC address of uplink device
                "uri": ""                      # URI to the device on the controller
            },
            "guid": None,                      # Global Unique Identifier
            "anonymousDeviceId": "",           # Random ID when not adopted
            "lastMotion": 0,                   # Last motion event timestamp
            "micVolume": 100,                  # Microphone volume level
            "isMicEnabled": True,              # Whether microphone is enabled
            "isRecording": True,               # Whether the device is currently recording
            "isWirelessUplinkEnabled": True,   # Whether Wi-Fi uplink is enabled
            "isMotionDetected": False,         # Whether motion is currently being detected
            "isSmartDetected": False,          # Whether smart detect (e.g., person) is triggered
            "phyRate": 100,                    # Link rate in Mbps
            "hdrMode": True,                   # HDR video mode enabled
            "videoMode": "default",            # Camera's video profile
            "isProbingForWifi": False,         # Whether device is actively scanning for Wi-Fi
            "apMac": None,                     # MAC address of connected access point
            "apRssi": None,                    # RSSI from connected AP
            "apMgmtIp": None,                  # Management IP of AP
            "elementInfo": None,               # Internal metadata used by UI
            "elementInfo": None,               # Internal metadata used by UI
            "chimeDuration": 0,                # Duration of chime (e.g., for doorbell)
            "isDark": False,                   # Whether the current scene is dark (night mode)
            "lastRing": None,                  # Timestamp of the last doorbell ring
            "isLiveHeatmapEnabled": False,     # Whether heatmap overlay is enabled
            "eventStats": {                    # Statistics for motion/smart detections
                "motion": {
                    "today": 0,                # Motion events today
                    "average": 0,              # Average daily motion events
                    "lastDays": [0] * 7,       # Motion event counts over last 7 days
                    "recentHours": [0] * 13    # Motion event counts over past 13 hours
                },
                "smart": {
                    "today": 0,                # Smart detections today
                    "average": 0,              # Average smart detections
                    "lastDays": [0] * 7        # Smart detection counts over last 7 days
                }
            },
            "videoReconfigurationInProgress": False,  # Indicates if video settings are being applied
            "voltage": None,                   # Current power input (e.g. PoE voltage)
            "homekitAccessoryId": None,        # Unique ID for Apple HomeKit integration
            "activePatrolSlot": None,          # Currently active patrol slot for PTZ cams
            "hubMac": None,                    # MAC address of associated hub device (if any)
            "isPoorNetwork": False,            # Whether the device has poor network quality
            "stopStreamLevel": None,           # Stream level at which to stop streaming
            "downScaleMode": 0,                # Current downscale configuration
            "isExtenderInstalledEver": False,  # Whether an extender was ever installed
            "isWaterproofCaseAttached": False, # Whether waterproof case is attached
            "isMissingRecordingDetected": False,# Flag if any recordings are missing
            "userConfiguredAp": False,         # If user manually set up the AP
            "hasRecordings": True,             # Whether the device has stored recordings
            "videoCodec": "h264",              # Currently active video codec
            "videoCodecState": 0,              # Internal state of codec switching
            "videoCodecSwitchingSince": None,  # Time since codec switching started
            "videoCodecLastSwitchAt": None,    # Timestamp of last codec switch
            "enableNfc": False,                # Whether NFC is enabled (e.g. for access control)
            "isThirdPartyCamera": False,       # True if it's an ONVIF/third-party camera
            "isPairedWithAiPort": False,       # True if paired with an AI port device
            "streamingChannels": [],           # Streaming channel definitions
            "isAdoptedByAccessApp": False,     # Whether adopted by UniFi Access
            "ptzControlEnabled": True,         # Pan-tilt-zoom control enabled
            "hallwayMode": "disabled",         # Hallway view mode status
            "wiredConnectionState": {"phyRate": 100},  # Wired connection physical rate
            "wifiConnectionState": {           # Wi-Fi connection status
                "channel": None,
                "frequency": None,
                "phyRate": None,
                "txRate": None,
                "signalQuality": None,
                "ssid": None,
                "bssid": None,
                "apName": "",                  # Access Point name
                "experience": None,
                "signalStrength": None,
                "connectivity": None
            },
            "channels": [],                    # List of stream/video channels
            "ispSettings": {},                 # ISP-specific settings
            "audioSettings": {},               # Microphone/audio configurations
            "talkbackSettings": {},            # Two-way talk feature configuration
            "osdSettings": {},                 # On-screen display settings
            "ledSettings": {},                 # LED behavior settings
            "speakerSettings": {},             # Speaker volume/config
            "recordingSettings": {},           # Motion/schedule-based recording setup
            "smartDetectSettings": {},         # AI-based detection config
            "recordingSchedulesV2": [],        # Advanced recording schedule definitions
            "motionZones": [],                 # Motion detection zone definitions
            "privacyZones": [],                # Video privacy mask zones
            "smartDetectZones": [],            # Smart detection zone definitions
            "secondLensSmartDetectZones": [],  # Smart detection for dual lens
            "smartDetectLines": [],            # Smart detection lines (crossing lines)
            "smartDetectLoiterZones": [],      # Loitering detection zones
            "stats": {},                       # Performance and usage statistics
            "featureFlags": {},                # Feature toggles for experimental features
            "tiltLimitsOfPrivacyZones": {},    # Privacy tilt boundaries
            "lcdMessage": {},                  # LCD message configuration (e.g., doorbell screen)
            "lenses": [],                      # Multiple lens configuration
            "streamSharing": {},               # Public/private stream sharing settings
            "homekitSettings": {},             # Apple HomeKit integration settings
            "shortcuts": [],                   # User-defined shortcuts
            "alarms": {},                      # Alarm settings (doorbell or smart detection)
            "extendedAiFeatures": {},          # AI-based advanced feature settings
            "thirdPartyCameraInfo": {},        # Metadata for ONVIF/third-party cams
            "fingerprintSettings": {},         # Access control fingerprint config
            "fingerprintState": {},            # Fingerprint access state
            "nfcSettings": {},                 # NFC reader settings
            "nfcState": {},                    # Current NFC access state
            "accessDeviceMetadata": {},        # Metadata for access control devices
            "id": "",                          # Internal camera/device ID
            "nvrMac": "",                      # MAC address of the controller/NVR
            "displayName": "",                 # Display name shown in the Protect UI
            "isConnected": True,               # True if the device is currently online
            "platform": "",                    # Platform string (hardware type)
            "hasSpeaker": True,                # Whether the camera has a built-in speaker
            "hasWifi": False,                  # Whether Wi-Fi is supported
            "audioBitrate": 64000,             # Audio bitrate setting (bps)
            "canManage": False,                # If current user can manage the device
            "isManaged": False,                 # Whether device is fully managed/adopted
            "marketName": "",                  # Commercial model name
            "is4K": False,                     # True if supports 4K resolution
            "is2K": True,                      # True if supports 2K resolution
            "currentResolution": "2K",         # Active streaming resolution
            "supportedScalingResolutions": ["HD", "2K"],  # List of resolutions that can be downscaled to
            "hdrType": "auto",                 # HDR configuration (e.g., auto, on, off)
            "aiPortCapacityPoints": 0.25,      # AI port usage capacity
            "modelKey": "camera"               # Unique type key in the UniFi API system
        }

    def __getitem__(self, key):
        """
        Thread-safe read access to a setting.

        Usage:
            value = settings["isConnected"]
        """
        with self._lock:
            return self.settings[key]

    def __setitem__(self, key, value):
        """
        Thread-safe write access to a setting. Automatically persists to disk.

        Usage:
            settings["isUpdating"] = True
        """
        with self._lock:
            self.settings[key] = value
            self._save()

    def __contains__(self, key):
        """
        Thread-safe key existence check.

        Usage:
            if "mac" in settings:
                ...
        """
        with self._lock:
            return key in self.settings

    def get(self, key, default=None):
        """
        Thread-safe retrieval with fallback.

        Usage:
            mac = settings.get("mac", "00:00:00:00:00:00")
        """
        with self._lock:
            return self.settings.get(key, default)

    def update(self, updates: dict):
        """
        Thread-safe bulk update. Automatically persists to disk.

        Usage:
            settings.update({
                "firmwareVersion": "v5.0.0",
                "isUpdating": False
            })
        """
        with self._lock:
            self.settings.update(updates)
            self._save()

    def _save(self):
        with self._lock:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=2)

    def _get_nested_value(self, dotted_key, default=None):
        """
        Safely gets a nested value like 'uplinkDevice.mac'.
        Returns `default` if any part of the path is missing.
        """
        keys = dotted_key.split(".")
        value = self.settings
        for key in keys:
            if not isinstance(value, dict):
                return default
            value = value.get(key, default)
            if value is default:
                break
        return value

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
        if mac_str:
            return bytes.fromhex(mac_str.replace(":", ""))
        return None


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
        if ip_str:
            try:
                return socket.inet_aton(ip_str)
            except OSError:
                return None
        return None
