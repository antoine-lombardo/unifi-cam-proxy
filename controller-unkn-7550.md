Service: `ms`

Command: `/usr/bin/ms /usr/share/ms/ms.json`

Listening to: `192.168.1.1:7550`

`/usr/share/ms/ms.json`
```
{
    "daemon": false,
    "pathSeparator": "/",
    "logAppenders": [
      {
        "name": "file appender",
        "type": "file",
        "level": 3,
        "fileName": "/srv/ms/logs/ms",
        "newLineCharacters": "\n",
        "fileHistorySize": 5,
        "fileLength": 10485760,
        "singleLine": true
      },
      {
        "name": "file appender",
        "type": "file",
        "level": 2,
        "fileName": "/srv/ms/logs/ms.err",
        "newLineCharacters": "\n",
        "fileHistorySize": 2,
        "fileLength": 10485760,
        "singleLine": true
      }
    ],
    "applications": [
      {
        "appDir": "./",
        "name": "evostreamms",
        "description": "Media Server",
        "protocol": "dynamiclinklibrary",
        "default": true,
        "maxWaitForTracksPeriod": 10000,
        "streamsExpireTimer": 10,
        "rtcpDetectionInterval": 1,
        "hasStreamAliases": true,
        "hasIngestPoints": true,
        "validateHandshake": false,
        "aliases": [
          "er",
          "live",
          "vod"
        ],
        "maxRtmpOutBuffer": 524288,
        "maxRtspOutBuffer": 2097152,
        "pushPullPersistenceFile": "/dev/null",
        "authPersistenceFile": "/dev/null",
        "connectionsLimitPersistenceFile": "/dev/null",
        "bandwidthLimitPersistenceFile": "/dev/null",
        "ingestPointsPersistenceFile": "/dev/null",
        "streamAliasesPersistenceFile": "/dev/null",
        "eventLogger": {
          "sinks": [
            {
              "type": "rpc",
              "url": "ws://127.0.0.1:7080/ems",
              "serializerType": "JSON",
              "enabledEvents": [
                "inStreamCreated",
                "outStreamCreated",
                "inStreamClosed",
                "outStreamClosed",
                "rtspStreamNotFound"
              ]
            },
            {
              "type": "msr",
              "url": "localhost:7700",
              "enabledEvents": [
                "recordChunkClosed",
                "recordChunkError"
              ]
            }
          ]
        },
        "acceptors": [
          {
            "ip": "127.0.0.1",
            "port": 7440,
            "protocol": "inboundWsJsonCli",
            "useLengthPadding": true
          },
          {
            "ip": "127.0.0.1",
            "port": 1112,
            "protocol": "inboundJsonCli",
            "useLengthPadding": true
          },
          {
            "ip": "0.0.0.0",
            "port": 7445,
            "protocol": "inboundWsStreaming"
          },
          {
            "ip": "0.0.0.0",
            "port": 7451,
            "protocol": "inboundTcpStreaming"
          },
          {
            "ip": "0.0.0.0",
            "port": 7446,
            "protocol": "inboundWssStreaming",
            "sslKey": "/data/unifi-core/config/unifi-core.key",
            "sslCert": "/data/unifi-core/config/unifi-core.crt",
            "cipherSuite": "HIGH:!aNULL@STRENGTH"
          },
          {
            "ip": "0.0.0.0",
            "port": 7550,
            "protocol": "inboundLiveFlv",
            "maxInboundFrameSize": 4194304,
            "waitForMetadata": 5
          },
          {
            "ip": "0.0.0.0",
            "port": 7552,
            "protocol": "inboundLiveFlvs",
            "maxInboundFrameSize": 4194304,
            "waitForMetadata": 5,
            "sslKey": "/data/unifi-core/config/unifi-core.key",
            "sslCert": "/data/unifi-core/config/unifi-core.crt",
            "cipherSuite": "HIGH:!aNULL@STRENGTH",
            "certvalidation": "strict"
          },
          {
            "ip": "0.0.0.0",
            "port": 7447,
            "protocol": "inboundRtsp"
          },
          {
            "ip": "0.0.0.0",
            "port": 7441,
            "protocol": "inboundRtsps",
            "sslKey": "/data/unifi-core/config/unifi-core.key",
            "sslCert": "/data/unifi-core/config/unifi-core.crt"
          }
        ]
      }
    ]
  }
```
