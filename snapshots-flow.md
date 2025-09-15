
## 1. Controller asks the camera for a snapshot (WSS port 7442)

`rel. time: 0.000ms`
`abs. time: 431.698269s`
`ref: 255342`

```json
{"from":"UniFiVideo","to":"ubnt_avclient","responseExpected":true,"functionName":"GetRequest","messageId":10102,"inResponseTo":0,"payload":{"what":"snapshot","uri":"https://10.30.50.1:7444/internal/camera-upload/DDUmF8TTL0JWZ8iJoPUYwyJPYrlzdNTL","timeoutMs":60000,"quality":"medium"}}
```

## 2. Camera generates the snapshot internally then respond to the controller (WSS port 7442)

`rel. time: 137.690ms`
`abs. time: 431.835959s`
`ref: 255465`

```json
{"from":"ubnt_avclient","functionName":"GetRequest","inResponseTo":10102,"messageId":51329540,"payload":{"payload":null},"responseExpected":false,"statusCode":0,"timeStamp":"2025-09-15T20:46:02.533+00:00","to":"UniFiVideo"}
```

## 3. Camera send snapshot to controller (HTTPS port 7444)

`rel. time: 562.240ms`
`abs. time: 432.260509s`
`ref: 256181`

```http
POST /internal/camera-upload/DDUmF8TTL0JWZ8iJoPUYwyJPYrlzdNTL HTTP/1.1
Host: 10.30.50.1:7444
Accept: */*
Content-Length: 251406
Content-Type: multipart/form-data; boundary=------------------------9c29bb6a226f9e14
Expect: 100-continue

--------------------------9c29bb6a226f9e14
Content-Disposition: form-data; name="payload"

**JPEG image binary**
--------------------------9c29bb6a226f9e14--
```

## 4. Controller responds

`rel. time: 564.592ms`
`abs. time: 432.262861s`
`ref: 256183`

```http
HTTP/1.1 200 OK
Content-Security-Policy: default-src 'self';base-uri 'self';block-all-mixed-content;font-src 'self' https: data:;frame-ancestors 'self';img-src 'self' data:;object-src 'none';script-src 'self';script-src-attr 'none';style-src 'self' https: 'unsafe-inline';upgrade-insecure-requests
Cross-Origin-Resource-Policy: same-site
X-DNS-Prefetch-Control: off
Expect-CT: max-age=0
X-Frame-Options: SAMEORIGIN
Strict-Transport-Security: max-age=15552000; includeSubDomains
X-Download-Options: noopen
X-Content-Type-Options: nosniff
X-Permitted-Cross-Domain-Policies: none
Referrer-Policy: strict-origin-when-cross-origin
X-XSS-Protection: 0
Vary: Origin
Access-Control-Allow-Credentials: true
Content-Type: application/json; charset=utf-8
Content-Length: 16
ETag: W/"10-oV4hJxRVSENxc/wX8+mA4/Pe4tA"
Date: Mon, 15 Sep 2025 20:46:02 GMT
Connection: keep-alive
Keep-Alive: timeout=5

{"success":true}
```
