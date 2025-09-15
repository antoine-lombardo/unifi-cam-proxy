Service: `lighttpd`

Command: `/bin/lighttpd -D -f /etc/lighttpd.conf`

Listening to: `https://192.168.1.222:443`

`/etc/lighttpd.conf`
```
server.document-root = "/usr/www"
static-file.disable-pathinfo = "enable"
include "/usr/etc/lighttpd/modules.conf"
include "/usr/etc/lighttpd/mimetypes.conf"
include "/usr/etc/lighttpd/lighttpd.conf"

server.modules += ( "mod_access" , "mod_redirect" )

$SERVER["socket"] == ":443" {
protocol = "https://"
ssl.engine = "enable"
ssl.disable-client-renegotiation = "enable"
ssl.pemfile = "/etc/server.pem"
ssl.ec-curve = "prime256v1"
ssl.use-sslv2 = "disable"
ssl.use-sslv3 = "disable"
ssl.honor-cipher-order = "enable"
ssl.cipher-list = "ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256"
} else $HTTP["scheme"] == "http" {
    $HTTP["url"] !~ "^/snap.jpeg$" {
        $HTTP["host"] =~ ".*"  {
             url.redirect = ( ".*" => "https://%0" )
        }
    }
}
```


## Login Request

### Request from controller

`abs. time: 282.699836s`
`ref: 165541`

```http
POST /api/1.2/login HTTP/1.1
Host: 192.168.1.222
Content-Type: application/json
Content-Length: 53
Connection: keep-alive

{"username":"ubnt","password":"********************"}

```

### Response from camera

`abs. time: 285.512246s`
`ref: 167363`

```http
HTTP/1.1 200 OK
Content-Type: application/json
Set-Cookie: authId=******a5-****-****-****-********cd84; Path=/; Expires=Tue, 16 Sep 2025 20:43:36 GMT; Max-Age=86400; Version=1; HttpOnly
Connection: close
Cache-Control: no-store
Content-Length: 1819
Date: Mon, 15 Sep 2025 20:43:36 GMT
Server: lighttpd

{"board":{"hwaddr":"74******DB91","mac":"74:**:**:**:DB:91","maxTimeoutFwUpdate":150,"maxTimeoutReboot":30,"name":"UVC G3 Flex","sysid":42292},"controller":{"adopted":true,"authToken":"846d********************************************************d479","controllerName":"","controllerVersion":"","host":"","port":0,"state":"CONNECTING_TO_CONTROLLER_WS","uuid":"****f011-****-****-****-********2b47"},"device":{"language":"en-US"},"features":{"accelerometer":1,"adjustableIR":0,"aec":0,"aecFullband":0,"aecNarrowband":0,"aecTalkbackSwitch":false,"aecWideband":0,"audioCodecs":["aac","opus"],"autoICROnly":1,"battery":0,"bluetooth":0,"chimeControl":0,"endlesspan":0,"externalIR":0,"externalIRAutodetect":0,"fingerprint":0,"fisheye":false,"flash":false,"fullHdSnapshot":true,"hdr":1,"hotplug":{"extender":{"attached":false}},"lcdScreen":0,"ldc":1,"ledIr":1,"ledStatus":1,"lineIn":0,"luxCheck":false,"magicZoom":0,"mic":1,"motionDetect":["enhanced"],"nfc":0,"opticalZoom":0,"opusSampleRates":[12000,16000,24000,48000],"pirMotionDetect":0,"presetTour":false,"privacyMask":1,"privacyMasks":{"maxZones":16,"rectangleOnly":false},"ptz":0,"resetIC":0,"rtc":0,"rtsp":1,"sdmmc":0,"smartDetect":[],"speaker":0,"squareEventThumbnail":true,"supportCustomRingtone":false,"touchFocus":0,"truedaynight":1,"verticalFlipWarning":false,"videoCodecs":["h264","mjpg"],"videoMode":["default","sport","slowShutter"],"videoSourceCount":1,"wifi":0},"fw":{"protocolVer":67,"semver":"4.75.62","version":"UVC.v4.75.62.67.e71c6e5.250411.1421"},"hostName":"****","network":{"bytesRx":693464761,"bytesTx":2649473813,"dns":"192.168.1.1","gw":"192.168.1.1","ip":"192.168.1.222","leaseTime":86400,"mask":"255.255.255.0","nic":"eth0","speed":100},"request":{"remoteIp":"192.168.1.1"},"system":{"cpu":84,"loadavg":2.035645,"uptime":3126955},"wifi":null}

```




## Connect Request

### Request from controller

`abs. time: 285.727600s`
`ref: 167525`

```http
POST /api/1.2/connect HTTP/1.1
Host: 192.168.1.222
Cookie: authId=******a5-****-****-****-********cd84; Expires=Tue, 16 Sep 2025 20:43:36 GMT; Max-Age=86400; Path=/; HttpOnly; Version=1
Content-Type: application/json
Content-Length: 53
Connection: keep-alive

{"username":"ubnt","password":"********************"}

```

### Response from camera

`abs. time: 287.385786s`
`ref: 168729`

```http
HTTP/1.1 200 OK
Connection: close
Cache-Control: no-store
Content-Length: 0
Date: Mon, 15 Sep 2025 20:43:38 GMT
Server: lighttpd

```

