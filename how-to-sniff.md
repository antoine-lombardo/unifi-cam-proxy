# How to sniff traffic between the controller and the camera

## 1. SSH into to the controller (i.e. UDM Pro / UDM SE)

From the Unifi UI:

`Network` -> `Settings` -> `Control Plane` -> `Console` -> Check `SSH` -> `Change Password`

Then connect to `root@{controller-ip}:22`

## 2. Stop the Unifi Protect service

```shell
systemctl stop unifi-protect
```

## 3. Modify the service file

```shell
nano /lib/systemd/system/unifi-protect.service
```

Change the following line: `ExecStart=/bin/bash -c "/usr/bin/node20 --expose-gc --max-old-space-size=$UFP_MAX_OLD_SPACE --v8-pool-size=16 --no-use-idle-notification --no-network-family-autoselection --dns-result-order=ipv4first --title=unifi-protect /usr/share/unifi-protect/app/service.js"`

To: `ExecStart=/bin/bash -c "/usr/bin/node20 --tls-keylog /tmp/unifiprotectsslkeys.log --expose-gc --max-old-space-size=$UFP_MAX_OLD_SPACE --v8-pool-size=16 --no-use-idle-notification --no-network-family-autoselection --dns-result-order=ipv4first --title=unifi-protect /usr/share/unifi-protect/app/service.js"`

## 4. Reload services & restart Unifi Protect

```shell
systemctl daemon-reload
systemctl start unifi-protect
```

## 5. Sniff traffic remotely using Wireshark

Inside Git Bash:

```shell
ssh root@{controller-ip} "sudo tcpdump -U -s0 -i eth10 -w - src host {camera-ip} or dst host {camera-ip}" | "/C/Program Files/Wireshark/Wireshark.exe" -k -i -
```

Capture as long as needed, then save as `.pcapng`. Close Wireshark then reload the saved file in another window.

## 6. Decrypt traffic

Download SSL log file from the controller through SFTP. Log file is located in `/tmp/unifiprotectsslkeys.log`.

In Wireshark, load the log file: `Edit` -> `Preferences` -> `Protocols` -> `TLS` -> `(Pre)-Master-Secret log filename`.

Once loaded, HTTPS and WSS traffic should show in cleartext. If not working, the log file might not include the required keys. Download a newer version of it and retry.
