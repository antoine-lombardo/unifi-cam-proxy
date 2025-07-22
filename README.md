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

## Roadmap
- [x] Device Discovery
  - [ ] Document `1284` – Maps camera system IDs to camera types, platforms, and GUIDs
  - [ ] Document `13701` – UniFi Protect discovery scanner logic
  - [ ] Document `42942` – DeviceType model structure
  - [ ] Document `13701` – Discovery field types and helper functions
- [ ] Camera Adoption
  - [ ] Handle `POST /api/1.2/manage`
  - [ ] Implement ongoing API message handling
- [ ] RTSP Stream
  - [ ] Simulate RTSP stream output
  - [ ] Handle motion detection event simulation


## Documentation

~~View the documentation at <https://unifi-cam-proxy.com>~~

Due to significant changes in UniFi Protect, this project is being rewritten from the ground up.  
While the core functionality will remain the same, several improvements and enhancements are planned.

## UniFi Protect Discovery & Adoption Process

UniFi Protect discovers camera devices by sending a UDP message to candidates on **port `10001`**.

---

### Discovery Request

**Received Discovery Message:**

```
Raw: 01 00 00 00
```

| Field     | Size   | Description                       |
|-----------|--------|-----------------------------------|
| VERSION   | 1 byte | Always `0x01`                     |
| CMD       | 1 byte | Always `0x00` (discovery request) |
| LEN       | 2 bytes| Payload length (usually `0x0000`) |

---

### Expected Discovery Response Structure

| Field Name                   | Type          | ID (Type) | Format / Note                          |
|------------------------------|---------------|-----------|----------------------------------------|
| `VERSION`                    | UInt8         | —         | Always 1                               |
| `CMD`                        | UInt8         | —         | Always 0                               |
| `LEN`                        | UInt16        | —         | Byte length of payload                 |
| `HWADDR`                     | MAC           | `0x01`    | 6 bytes                                |
| `HOSTNAME`                   | Null-Term Str | `0x11`    | e.g., `"Front-Door"`                   |
| `PLATFORM`                   | Null-Term Str | `0x0C`    | e.g., `"UniFiOS"`                      |
| `WMODE`                      | UInt8         | `0x0E`    | `1` = Wired, `2` = Wireless            |
| `ESSID`                      | Null-Term Str | `0x0D`    | e.g., `"SSID"`                         |
| `FWVERSION`                  | Null-Term Str | `0x03`    | e.g., `"5.0.129"`                      |
| `DEVICE_ID`                  | Null-Term Str | `0x20`    | UUID (text), e.g., `"a99e...4360"`     |
| `UPTIME`                     | UInt32        | `0x0A`    | Uptime in seconds                      |
| `WEBUI`                      | 4 bytes       | `0x0F`    | HTTPS? (2 bytes), port (2 bytes)       |
| `PRIMARY_ADDRESS`            | MAC+IP (10B)  | `0x2F`    | MAC (6) + IP (4)                       |
| `SYSTEM_ID`                  | UInt16 (LE)   | `0x10`    | Little-endian camera system ID         |
| `MODEL`                      | Null-Term Str | `0x20`    | Full model name, e.g.,`"UVC G4 Bullet"`|
| `MODEL_SHORT`                | Null-Term Str | `0x21`    | Short name, e.g., `"G4 Bullet"`        |
| `DEVICE_DEFAULT_CREDENTIALS` | UInt8         | `0x2C`    | `1` = default credentials              |
| `GUID`                       | 16 bytes      | `0x2B`    | Unique camera identifier               |
| `CONTROLLER_ID`              | 16 bytes      | `0x26`    | Unique controller identifier           |
| `CUSTOM_UNIFI_FIELDS` (opt)  | TLV           | `0x82`    | Subfields like BLE bridge info         |

---

### Adoption Flow

If the camera is discovered, it will appear in the **UniFi Protect** UI.  
Click **"Add"** to add the device, then **"Adopt"** to begin management.

---

### Sample Adoption Request

Once adopted, the controller will send the following request:

```http
POST /api/1.2/manage
```
Payload Example:
```
{
  "username": "ubnt",
  "password": "ubnt",
  "mgmt": {
    "username": "ubnt",
    "password": "ubnt",
    "hosts": ["***.***.***.***:7442"],
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


## Donations

If you would like to make a donation to support development, please use [Github Sponsors](https://github.com/sponsors/keshavdv).
