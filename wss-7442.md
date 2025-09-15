

## 1. Camera requests WSS connection (HTTPS port 7442)

`rel. time: 0.000ms`
`abs. time: 286.652800s`
`ref: 168306`

```http
GET /camera/1.0/ws HTTP/1.1
Pragma: no-cache
Cache-Control: no-cache
Host: 192.168.1.1
Origin: http://ws_camera_proto_secure_transfer
Upgrade: websocket
Connection: close, Upgrade
Sec-WebSocket-Key: LG3S****************LQ==
Sec-WebSocket-Protocol: secure_transfer
Sec-WebSocket-Version: 13
Camera-MAC: 74******DB91
Camera-IP: 192.168.1.222
Camera-Model: 0xa534
Camera-Firmware: 4.75.62
Device-ID: ********-****-****-****-************
Adopted: true


```

## 2. Controller upgrades to WSS

`rel. time: 40.426ms`
`abs. time: 286.693226s`
`ref: 168332`

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: ************************6k4=
Sec-WebSocket-Protocol: secure_transfer


```

## 3. INFO events

`rel. time: 170.576ms`
`abs. time: 286.823376s`
`ref: 168390`

```json
["info","Connection 0939819582: changing state 'connecting' -> 'connected' [ubnt_avclient:connection_state.cpp:SetState:28]",{"datetime":"2025-09-15T20:43:37Z","ident":"avclient","pid":783,"uptime":"1270142308,680"}]
```


`rel. time: 182.275ms`
`abs. time: 286.835075s`
`ref: 168392`

```json
["info","Connected to UniFi Video WS. [ubnt_avclient:avclient_app.cpp:Service:1059]",{"datetime":"2025-09-15T20:43:37Z","ident":"avclient","pid":783,"uptime":"1270142308,682"}]
```

... a lot more

## 4. Time sync requests (10 requests/responses)

`rel. time: 189.419ms`
`abs. time: 286.842219s`
`ref: 168406`

```json
{"from":"ubnt_avclient","functionName":"ubnt_avclient_timeSync","inResponseTo":0,"messageId":51329504,"payload":{"timeDelta":0},"responseExpected":true,"timeStamp":"2025-09-15T20:43:37.538+00:00","to":"UniFiVideo"}
```

`rel. time: 198.691ms`
`abs. time: 286.851491s`
`ref: 168415`

```json
{"from":"UniFiVideo","to":"ubnt_avclient","responseExpected":false,"functionName":"ubnt_avclient_timeSync","messageId":10000,"inResponseTo":51329504,"payload":{"t1":1757969017574,"t2":1757969017574}}
```

`rel. time: 254.801ms`
`abs. time: 286.907601s`
`ref: 168437`

```json
{"from":"ubnt_avclient","functionName":"ubnt_avclient_timeSync","inResponseTo":10000,"messageId":51329505,"payload":{"timeDelta":0},"responseExpected":true,"timeStamp":"2025-09-15T20:43:37.603+00:00","to":"UniFiVideo"}
```

`rel. time: 277.534ms`
`abs. time: 286.930334s`
`ref: 168461`

```json
{"from":"UniFiVideo","to":"ubnt_avclient","responseExpected":false,"functionName":"ubnt_avclient_timeSync","messageId":10001,"inResponseTo":51329505,"payload":{"t1":1757969017654,"t2":1757969017654}}
```

... 7 requests/responses not shown

`rel. time: 779.722ms`
`abs. time: 287.432522s`
`ref: 168772`

```json
{"from":"ubnt_avclient","functionName":"ubnt_avclient_timeSync","inResponseTo":10009,"messageId":51329513,"payload":{"timeDelta":0},"responseExpected":true,"timeStamp":"2025-09-15T20:43:38.123+00:00","to":"UniFiVideo"}
```

`rel. time: 781.808ms`
`abs. time: 287.434608s`
`ref: 168773`

```json
{"from":"UniFiVideo","to":"ubnt_avclient","responseExpected":false,"functionName":"ubnt_avclient_timeSync","messageId":10010,"inResponseTo":51329513,"payload":{"t1":1757969018158,"t2":1757969018158}}
```

## 5. Hello

`rel. time: 1121.806ms`
`abs. time: 287.774606s`
`ref: 168988`

```json
{"from":"ubnt_avclient","functionName":"ubnt_avclient_hello","inResponseTo":0,"messageId":51329514,"payload":{"adoptionCode":"","connectionHost":"192.168.1.1","connectionSecurePort":7442,"features":{"accelerometer":true,"adjustableIR":false,"aec":[],"aecTalkbackSwitch":false,"audioCodecs":["aac","opus"],"autoICROnly":true,"battery":false,"bluetooth":false,"chimeControl":false,"doorAccessConfig":false,"endlesspan":false,"externalIR":false,"externalIRAutodetect":false,"fingerprint":false,"fisheye":false,"flash":false,"fullHdSnapshot":true,"hallwayMode":false,"hdr":true,"hotplug":{"extender":{"attached":false}},"lcdScreen":false,"ldc":true,"ledIR":true,"ledStatus":true,"lineIn":false,"luxCheck":false,"magicZoom":false,"maxScaleDownLevel":0,"mic":true,"motionDetect":["enhanced"],"nfc":false,"opticalZoom":false,"opusSampleRates":[12000,16000,24000,48000],"pirMotionDetect":false,"presetTour":false,"privacyMask":true,"privacyMasks":{"maxZones":16,"rectangleOnly":false},"ptz":false,"resetIC":false,"rtc":false,"sdmmc":false,"smokeCover":false,"speaker":false,"squareEventThumbnail":true,"streamEncryptable":false,"supportCustomRingtone":false,"touchFocus":false,"truedaynight":true,"verticalFlipWarning":false,"videoCodecs":["h264","mjpg"],"videoMode":["default","sport","slowShutter"],"videoModeMaxFps":[25,25,20],"videoSourceCount":1,"wifi":false},"fwVersion":"UVC.S2L.v4.75.62.67.e71c6e5.250411.1421","hwrev":8,"ip":"192.168.1.222","mac":"74******DB91","model":"UVC G3 Flex","name":"G3 Flex","protocolVersion":67,"rebootTimeoutSec":30,"semver":"4.75.62","upgradeTimeoutSec":150,"uptime":3126957},"responseExpected":false,"timeStamp":"2025-09-15T20:43:38.458+00:00","to":"UniFiVideo"}
```

`rel. time: 1293.652ms`
`abs. time: 287.946452s`
`ref: 169077`

```json
{"from":"UniFiVideo","to":"ubnt_avclient","responseExpected":false,"functionName":"ubnt_avclient_hello","messageId":10013,"inResponseTo":51329514,"payload":{"protocolVersion":67,"controllerName":"****","controllerUuid":"********-****-****-****-************","controllerVersion":"6.1.68","overrideUuid":true}}
```

## 6. Parameters agreement

`rel. time: 1807.542ms`
`abs. time: 288.460342s`
`ref: 169418`

```json
{"from":"UniFiVideo","to":"ubnt_avclient","responseExpected":true,"functionName":"ubnt_avclient_paramAgreement","messageId":10037,"inResponseTo":0,"payload":{"enableStatusCodes":true,"useHeartbeats":false,"heartbeatsTimeoutMs":60000}}
```

`rel. time: 1984.035ms`
`abs. time: 288.636835s`
`ref: 169552`

```json
{"from":"ubnt_avclient","functionName":"ubnt_avclient_paramAgreement","inResponseTo":10037,"messageId":51329515,"payload":{"authToken":"7392********************************************************f613"},"responseExpected":false,"timeStamp":"2025-09-15T20:43:39.212+00:00","to":"UniFiVideo"}
```
