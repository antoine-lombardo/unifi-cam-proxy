[![unifi-cam-proxy Discord](https://img.shields.io/discord/937237037466124330?color=0559C9&label=Discord&logo=discord&logoColor=%23FFFFFF&style=for-the-badge)](https://discord.gg/Bxk9uGT6MW)

# UniFi Camera Proxy

## About

This enables using non-Ubiquiti cameras within the UniFi Protect ecosystem. This is
particularly useful to use existing RTSP-enabled cameras in the same UI and
mobile app as your other Unifi devices.

Things that work:

* ~~Live streaming~~
* ~~Full-time recording~~
* ~~Motion detection with certain cameras~~
* ~~Smart Detections using [Frigate](https://github.com/blakeblackshear/frigate)~~

Due to significant changes in UniFi Protect, this project is currently being rewritten.
While the core functionality will remain the same, several improvements are planned — including better support for adoption, motion events, and PTZ controls.

## Roadmap
- [x] Device Discovery
- [x] Camera Adoption
  - [x] Handle `POST /api/1.2/manage`
  - [ ] Implement ongoing API message handling
- [ ] WSS
  - [ ] 🛑 WSS adoption handshake (currently missing endpoint)
  - [ ] Simulate RTSP stream output
  - [ ] 38934 Handle motion detection event simulation and PTZ

## Starting The Dev Container
To get started:
1. Clone the repository using Git to a folder on a Linux machine with Docker installed.
2. Remote into the machine and open the folder using Visual Studio Code.
3. Create a custom Docker network using macvlan (see instructions below).
4. When prompted, allow VS Code to build and open the dev container.
You can also rebuild the container at any time by pressing <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>P</kbd> and selecting "Dev Containers: Rebuild Container".
5. Once the container is running and UniFi Protect is active on the same network, a discovery message should be recieved automatically.
After the script responds to the discovery message (within 10–20 seconds), a new device should appear in UniFi Protect, ready for adoption.

Note: Before launching the dev container, you need to create a custom Docker network using macvlan:
```
docker network create -d macvlan \
  --subnet=192.168.0.0/24 \
  --gateway=192.168.0.1 \
  -o parent=lan0 \
  lan_net
```

Replace lan0 with your actual network interface name (e.g., eth0, enp3s0, etc.).

## Documentation

~~View the documentation at <https://unifi-cam-proxy.com>~~

## UniFi Protect Discovery & Adoption Process

**UniFi Protect** discovers compatible cameras by broadcasting a **UDP discovery message** to devices on **port `10001`**.

---

### 📡 Discovery Request

**Example Received Message:**

```
Raw: 01 00 00 00
```

| Field   | Size   | Description                         |
|---------|--------|-------------------------------------|
| VERSION | 1 byte | Always `0x01`                       |
| CMD     | 1 byte | Always `0x00` (discovery request)   |
| LEN     | 2 bytes| Payload length (usually `0x0000`)   |

---

### 📦 Expected Discovery Response Structure

| Field Name                   | Type          | ID (Type) | Notes / Examples                         |
|------------------------------|---------------|-----------|------------------------------------------|
| `VERSION`                    | UInt8         | —         | Always `1`                                |
| `CMD`                        | UInt8         | —         | Always `0`                                |
| `LEN`                        | UInt16        | —         | Total payload byte length                |
| `HWADDR`                     | MAC           | `0x01`    | 6-byte MAC address                       |
| `HOSTNAME`                   | Null-Term Str | `0x11`    | e.g., `"Front-Door"`                     |
| `PLATFORM`                   | Null-Term Str | `0x0C`    | e.g., `"UniFiOS"`                        |
| `WMODE`                      | UInt8         | `0x0E`    | `1` = Wired, `2` = Wireless              |
| `ESSID`                      | Null-Term Str | `0x0D`    | e.g., `"MyWiFiSSID"`                     |
| `FWVERSION`                  | Null-Term Str | `0x03`    | e.g., `"5.0.129"`                        |
| `DEVICE_ID`                  | Null-Term Str | `0x20`    | UUID string, e.g., `"a99e...4360"`       |
| `UPTIME`                     | UInt32        | `0x0A`    | Uptime in seconds                        |
| `WEBUI`                      | 4 bytes       | `0x0F`    | 2 bytes for HTTPS flag, 2 for port       |
| `PRIMARY_ADDRESS`            | MAC+IP (10B)  | `0x2F`    | MAC (6 bytes) + IP (4 bytes)             |
| `SYSTEM_ID`                  | UInt16 (LE)   | `0x10`    | Camera system ID in little-endian        |
| `MODEL`                      | Null-Term Str | `0x20`    | e.g., `"UVC G4 Bullet"`                  |
| `MODEL_SHORT`                | Null-Term Str | `0x21`    | e.g., `"G4 Bullet"`                      |
| `DEVICE_DEFAULT_CREDENTIALS` | UInt8         | `0x2C`    | `1` = device has default credentials     |
| `GUID`                       | 16 bytes      | `0x2B`    | Optional Globally Unique Identifier for camera    |
| `CONTROLLER_ID`              | 16 bytes      | `0x26`    | Unique ID of the UniFi controller        |
| `CUSTOM_UNIFI_FIELDS` (opt)  | TLV           | `0x82`    | Optional nested fields (e.g., BLE info)  |

---

### ✅ Adoption Flow

Once the controller receives a valid response, the camera will appear in the **UniFi Protect** UI as **ready for adoption**.

Click **"Adopt"** to begin managing the camera.

---

### 🔐 Adoption Request Payload

After clicking "Adopt", the controller sends a management request to the camera:

```http
POST /api/1.2/manage
```

**Sample Payload:**
```json
{
  "username": "ubnt",
  "password": "ubnt",
  "mgmt": {
    "username": "ubnt",
    "password": "ubnt",
    "hosts": ["192.168.0.1:7442"],
    "token": "********************************",
    "protocol": "wss",
    "mode": 0,
    "nvr": "UDM-PRO",
    "controller": "Protect",
    "consoleId": "****-****-****-****-************",
    "consoleName": "My Console"
  }
}
```

 TODO

- Summarize the WSS handshake and message exchange once camera emulation is complete.
- Document the WebSocket message types and structure used by UniFi Protect.
- Add sample RTSP stream info if relevant.


# Advanced
Unifi protect main file is services.js. this file handles multiple services and functions.

| Port | Protocol | Purpose (likely)                                     | Direction                                                                |
| ---- | -------- | ---------------------------------------------------- | ------------------------------------------------------------------------ |
| 7080 | TCP      | UniFi Protect Camera HTTP API                        | **Camera → Controller** *(polls config, sends status, etc.)*             |
| 7440 | TCP      | Internal Protect messaging (likely microservice bus) | **Internal** *(Controller internal)*                                     |
| 7441 | TCP      | WSS for device telemetry & control (bi-directional)  | **Controller ↔ Camera**                                                  |
| 7442 | TCP6     | WSS Camera Registration (primary handshake)          | **Camera → Controller** *(camera initiates WSS)*                         |
| 7443 | TCP6     | Possibly legacy WSS or admin session                 | **Controller ↔ Camera/Admin** *(uncertain—possibly legacy)*              |
| 7444 | TCP6     | Possibly internal service communication              | **Internal** *(Controller internal)*                                     |
| 7450 | TCP      | Possibly firmware update / camera events             | **Controller → Camera** *(pushes updates or commands)*                   |
| 7005 | TCP      | Internal HTTP service or status                      | **Internal / Controller → Camera** *(used in some provisioning replies)* |
| 10001 | TCP     | Discovery message                                    | **Controller → Camera**                                                  |

Note: Some ports (e.g., 7442) may appear as TCP6. If your controller supports dual-stack networking, IPv4 connections will be correctly handled by these IPv6 sockets through IPv4-mapped IPv6 addresses.
- If bindv6only = 0: Dual-stack is enabled. A tcp6 socket bound to :: accepts both IPv6 and IPv4 connections (via ::ffff:x.x.x.x).
- If bindv6only = 1: The socket is IPv6-only. You will need a separate IPv4 listener to accept IPv4 connections.

To check your system's setting:
```
cat /proc/sys/net/ipv6/bindv6only
```
## Normal Operation
during normal operation you cammera maintains active connection to 3 ports: 7750, 7442 and 7444

- 3 simultaneous connections to 7550
- 2 simultaneous connections to 7442 this is the wss connection
- 1 connection to 7444 when viewing a camera live stream
```
ss -tnp | grep 'replace_with_your_camera_IP'
```

## Camera adoption sequance
| Step | Direction           | Port   | Protocol  | Purpose                           | Replicated  |
| ---- | ------------------- | ------ | --------- | --------------------------------- | ------------|
| 1    | Controller → Camera | 10001  | UDP       | Discovery                         | ✅          |
| 2    | Controller → Camera | 443    | HTTPS     | Adoption command (manage)         | ✅          |
| 3    | Camera → Controller | 7442   | WSS       | Authenticated WebSocket handshake |             |
| 4    | Controller → Camera | 7442   | WSS       | Sends settings + adoption details |             |
| 5a   | Camera → Controller | 7447 | RTSP     | Raw video stream (depends on config) |             |
| 5b   | Controller ↔ Camera | 7550 | WSS      | Event messages, status, commands     |             |

# UniFi Camera FLV & extendedFlv Stream Format

This document explains the structure of UniFi Protect's camera video stream format, which builds on standard FLV with extended metadata and custom event tagging.

---

## ⚙️ FLV Header Structure

| Bytes     | Field        | Type      | Default/Value | Description                             |
| --------- | ------------ | --------- | ------------- | --------------------------------------- |
| 0x00-0x02 | Signature    | `byte[3]` | `"FLV"`       | Magic bytes identifying an FLV stream   |
| 0x03      | Version      | `uint8`   | `0x01`        | FLV version number                      |
| 0x04      | Flags        | `uint8`   | `0x05`        | Bitmask: `0x04` = audio, `0x01` = video |
| 0x05-0x08 | Header Size  | `uint32`  | `0x00000009`  | Usually 9 bytes                         |
| 0x09-0x0C | PrevTagSize0 | `uint32`  | `0x00000000`  | Always zero at the start                |

---

## 🧹 Script Tag (extendedFlv Metadata)

The first tag after the FLV header is usually a Script/Data tag with custom UniFi metadata.

| Field          | Type     | Description                          |
| -------------- | -------- | ------------------------------------ |
| Tag Type       | `uint8`  | `0x12` = Script/Metadata tag         |
| Data Size      | `uint24` | Length of the AMF-encoded body       |
| Timestamp      | `uint24` | Usually 0                            |
| Timestamp Ext. | `uint8`  | Usually 0                            |
| Stream ID      | `uint24` | Always 0                             |
| Body           | AMF0     | Contains the string `"extendedFlv"`  |
| PrevTagSize    | `uint32` | Size of the full tag (header + body) |

**Example (AMF) body:**

```json
[
  "extendedFlv",
  {
    "streamName": "{7QuzFcivSjJFwnPN}",
    "withOpus": true,
    "withTalkback": true
  }
]
```

---

## 🎮 Audio & Video Tag Format

| Field          | Type     | Notes                          |
| -------------- | -------- | ------------------------------ |
| Tag Type       | `uint8`  | `0x08` = Audio, `0x09` = Video |
| Data Size      | `uint24` | Length of payload              |
| Timestamp      | `uint24` | Playback time                  |
| Timestamp Ext. | `uint8`  | High bits                      |
| Stream ID      | `uint24` | Always 0                       |
| Body           | `bytes`  | Codec-specific data            |
| PrevTagSize    | `uint32` | Length of full tag             |

---

## 🧠 Motion & Event Tags

Cameras embed motion or AI metadata as additional `0x12` script tags.

**Example:**

```json
[
  "event",
  {
    "motion": true,
    "zone": "default",
    "startTime": 1753081234.0,
    "endTime": 1753081240.0
  }
]
```

These tags are mixed between video/audio frames as real-time signals.

---

## ✅ Tag Summary

| Tag Type | Purpose           | Format     | Notes                              |
| -------- | ----------------- | ---------- | ---------------------------------- |
| `0x12`   | Metadata / Events | `AMF0`     | `extendedFlv`, motion events, etc. |
| `0x08`   | Audio             | AAC / Opus | Codec depends on stream settings   |
| `0x09`   | Video             | H.264      | Main stream video                  |

---

## 🧪 Stream Notes

- `extendedFlv` metadata appears immediately after the FLV header.
- Multiple `0x12` tags may be embedded for motion, license plate, or face events.
- Stream name is matched to the controller during handshake.
- Audio can be toggled by the controller (`suppressAudio`).

### Sample Hex Stream Breakdown

```hex
46 4C 56             ; Signature: "FLV"
01                   ; Version 1
05                   ; Flags: audio + video
00 00 00 09          ; Header size = 9

45 58 54 01          ; "EXT" + version 1

73 74 72 65 61 6D 31 32 33 34 ; "stream1234"
00 00 00 00 00 00             ; Padding

-- Metadata Tag --
12                   ; Script tag
00 00 15             ; Length
00 00 00 00          ; Timestamp
00 00 00             ; Stream ID
...                  ; JSON metadata

-- Video Tag --
09                   ; Video tag
00 00 08             ; Length
00 00 00 10          ; Timestamp: 16ms
00 00 00             ; Stream ID
17 01 00 00 00 FF D8 FF ; Mock video keyframe

-- Audio Tag --
08                   ; Audio tag
00 00 04             ; Length
00 00 00 20          ; Timestamp: 32ms
00 00 00             ; Stream ID
AF 01 12 34          ; AAC mock audio
```

---

## Donations

If you would like to make a donation to support development, please use [Github Sponsors](https://github.com/sponsors/keshavdv).
