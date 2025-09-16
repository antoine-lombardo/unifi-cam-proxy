# Complete adoption process

## 1. Discovery Request

Protocol: `UDP`
Source Host: `192.168.1.222 (Camera)`
Source Port: `10001`
Destination Host: `192.168.1.1 (Controller)`
Destination Port: `41117`


### Discovery Request Schema

| Field         | Size     | Description     | Type     |  Encoded Example | Decoded Example |
| ------------- | -------- | --------------- | -------- |----------------- | --------------- |
| VERSION       | 1 byte   | Always `0x01`   | UInt8    | `01`             | `1`             |
| COMMAND       | 1 byte   | Always `0x00`   | Enum     | `00`             | `CMD_INFO`      |
| Payload Size  | 2 bytes  | Payload Length  | UInt16BE | `00 9a`          | `154`           |
| Payload       | Variable | Payload Content |          |                  |                 |

### Discovery Payload Schema

| Field                              | Size     | Description                                             | Type     | Encoded Example                    | Decoded Example     |
| ---------------------------------- | -------- | ------------------------------------------------------- | -------- | ---------------------------------- | -------------------- |
| IPINFO - ID                        | 1 byte   | Always `0x02`                                           | Enum     | `02`                               | `IPINFO`             |
| IPINFO - Size                      | 2 bytes  | Always `0x000A`                                         | UInt16BE | `00 0A`                            | `10`                 |
| IPINFO - Mac Address               | 6 bytes  | Unifi Camera MAC Address, same as printed on the camera | N/A      | `74 ** ** ** DB 91`                | `74:**:**:**:DB:91`  |
| IPINFO - IP Address                | 4 bytes  | Unifi Camera IP Address, in hex format                  | N/A      | `C0 A8 01 DE`                      | `192.168.1.222`      |
| ETH_MAC_ADDR - ID                  | 1 byte   | Always `0x01`                                           | Enum     | `01`                               | `ETH_MAC_ADDR`       |
| ETH_MAC_ADDR - Size                | 2 bytes  | Always `0x0006`                                         | UInt16BE | `00 06`                            | `6`                  |
| ETH_MAC_ADDR - Value               | 6 bytes  | Same as `IPINFO - Mac Address`                          | N/A      | `74 ** ** ** DB 91`                | `74:**:**:**:DB:91`  |
| UPTIME - ID                        | 1 byte   | Always `0x0A`                                           | Enum     | `0A`                               | `UPTIME`             |
| UPTIME - Size                      | 2 bytes  | Always `0x0004`                                         | UInt16BE | `00 04`                            | `4`                  |
| UPTIME - Value                     | 4 bytes  | Camera uptime, in seconds                               | UInt32BE | `00 00 00 EA`                      | `234`                |
| HOSTNAME - ID                      | 1 byte   | Always `0x0B`                                           | Enum     | `0B`                               | `HOSTNAME`           |
| HOSTNAME - Size                    | 2 bytes  | Hostname String Length                                  | UInt16BE | `00 0B`                            | `11`                 |
| HOSTNAME - Value                   | Variable | Hostname String                                         | String   | `55 56 43 20 47 33 20 46 6C 65 78` | `UVC G3 Flex`        |
| PLATFORM - ID                      | 1 byte   | Always `0x0C`                                           | Enum     | `0C`                               | `PLATFORM`           |
| PLATFORM - Size                    | 2 bytes  | Platform String Length                                  | UInt16BE | `00 0B`                            | `11`                 |
| PLATFORM - Value                   | Variable | Platform String                                         | String   | `55 56 43 20 47 33 20 46 6C 65 78` | `UVC G3 Flex`        |
| MGMT_IS_DEFAULT - ID               | 1 byte   | Always `0x17`                                           | Enum     | `17`                               | `MGMT_IS_DEFAULT`    |
| MGMT_IS_DEFAULT - Size             | 2 bytes  | Always `0x0004`                                         | UInt16BE | `00 04`                            | `4`                  |
| MGMT_IS_DEFAULT - Value            | 4 bytes  | `0x0000` = Is Managed, `0x0001` = Not Managed           | N/A      | `00 00 00 01`                      | `Not Managed`        |
| FWVERSION - ID                     | 1 byte   | Always `0x03`                                           | Enum     | `03`                               | `FWVERSION`          |
| FWVERSION - Size                   | 2 bytes  | Firmware Version String Length                          | UInt16BE | `00 27`                            | `39`                 |
| FWVERSION - Value                  | Variable | Firmware Version String                                 | String   | `55 56 43 2E 53 32 4C 2E 76 34 2E 37 35 2E 36 32 2E 36 37 2E 65 37 31 63 36 65 35 2E 32 35 30 34 31 31 2E 31 34 32 31`  | `UVC.S2L.v4.75.62.67.e71c6e5.250411.1421` |
| SYSTEM_ID - ID                     | 1 byte   | Always `0x10`                                           | Enum     | `10`                               | `SYSTEM_ID`          |
| SYSTEM_ID - Size                   | 2 bytes  | Always `0x0002`                                         | UInt16BE | `00 02`                            | `2`                  |
| SYSTEM_ID - Value                  | 2 bytes  | System ID Hex Code                                      | UInt16LE | `34 A5`                            | `0xa534`             |
| DEVICE_ID - ID                     | 1 byte   | Always `0x20`                                           | Enum     | `20`                               | `DEVICE_ID`          |
| DEVICE_ID - Size                   | 2 bytes  | Device ID String Length                                 | UInt16BE | `00 24`                            | `36`                 |
| DEVICE_ID - Value                  | Variable | Device ID String                                        | String   | `39 37 64 35 ** ** ** ** 2D ** ** ** ** 2D ** ** ** ** 2D ** ** ** ** 2D ** ** ** ** ** ** ** ** 61 39 30 64` | `97d5****-****-****-****-********a90d`        |
| DEVICE_DEFAULT_CREDENTIALS - ID    | 1 byte   | Always `0x2C`                                           | Enum     | `2C`                               | `DEVICE_DEFAULT_CREDENTIALS` |
| DEVICE_DEFAULT_CREDENTIALS - Size  | 2 bytes  | Always `0x0001`                                         | UInt16BE | `00 01`                            | `1`                  |
| DEVICE_DEFAULT_CREDENTIALS - Value | 1 byte   | Default Credential Version                              | N/A      | `03`                               |                      |

### Complete Discovery Request

```
0000   01 00 00 9a 02 00 0a 74 ** ** ** db 91 c0 a8 01
0010   de 01 00 06 74 ** ** ** db 91 0a 00 04 00 00 00
0020   ea 0b 00 0b 55 56 43 20 47 33 20 46 6c 65 78 0c
0030   00 0b 55 56 43 20 47 33 20 46 6c 65 78 17 00 04
0040   00 00 00 01 03 00 27 55 56 43 2e 53 32 4c 2e 76
0050   34 2e 37 35 2e 36 32 2e 36 37 2e 65 37 31 63 36
0060   65 35 2e 32 35 30 34 31 31 2e 31 34 32 31 10 00
0070   02 34 a5 20 00 24 39 37 64 35 ** ** ** ** 2d **
0080   ** ** ** 2d ** ** ** ** 2d ** ** ** ** 2d ** **
0090   ** ** ** ** ** ** 61 39 30 64 2c 00 01 03
```

## 2. Discovery Response

