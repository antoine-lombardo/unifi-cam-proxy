from camera_data.camera_settings import CameraSettings
from discovery_responder import DiscoveryResponder
from api_server import VerboseAPIServer
import threading
import time

def increment_uptime(settings):
    while True:
        time.sleep(1)
        now_ms = int(time.time() * 1000)
        up_since = settings.get("upSince")
        if up_since:
            settings["uptime"] = int((now_ms - up_since) / 1000)

def main():
    settings = CameraSettings()

    now_ms = int(time.time() * 1000)

    # Start uptime thread
    settings.update({
        "upSince": now_ms,
        "lastSeen": None,
        "uptime": 0,
        "connectedSince": None
    })
    threading.Thread(target=increment_uptime, args=(settings,), daemon=True).start()
    print("[+] Uptime counter started")

    # Start discovery responder in its own thread
    if settings["canAdopt"]:
        responder = DiscoveryResponder(settings)
        threading.Thread(target=responder.start, daemon=True).start()
        print("[+] Discovery responder started")
    else:
        print("[-] Discovery responder skipped canAdopt = False")

    # Start HTTP API server on port 80
    api_server_80 = VerboseAPIServer(port=80, settings=settings)
    threading.Thread(target=api_server_80.start, daemon=True).start()

    # Start HTTPS API server on port 443 with SSL enabled
    api_server_443 = VerboseAPIServer(port=443, use_ssl=True, settings=settings)
    threading.Thread(target=api_server_443.start, daemon=True).start()

    # Keep main thread alive
    threading.Event().wait()

if __name__ == "__main__":
    main()
