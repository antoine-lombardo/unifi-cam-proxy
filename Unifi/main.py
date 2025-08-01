from camera_data.camera_settings import CameraSettings
from discovery_responder import DiscoveryResponder
from api_server import VerboseAPIServer
import threading
import time
import logging
import sys

def setup_logger(name="camera_app", level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s [%(threadName)s] [%(levelname)s] %(name)s: %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

def increment_uptime(settings, log):
    while True:
        time.sleep(1)
        now_ms = int(time.time() * 1000)
        up_since = settings.get("upSince")
        if up_since:
            settings["uptime"] = int((now_ms - up_since) / 1000)
        log.debug(f"Uptime updated: {settings['uptime']}s")

def main():
    log = setup_logger("main", logging.INFO)

    settings = CameraSettings()

    now_ms = int(time.time() * 1000)
    settings.update({
        "upSince": now_ms,
        "lastSeen": None,
        "uptime": 0,
        "connectedSince": None
    })

    # Start uptime thread with its own logger
    uptime_log = setup_logger("uptime", logging.INFO)
    threading.Thread(
        target=increment_uptime,
        args=(settings, uptime_log),
        daemon=True,
        name="UptimeThread"
    ).start()
    log.info("Uptime counter started")

    # Start discovery responder in its own thread
    if settings["canAdopt"]:
        responder = DiscoveryResponder(settings)
        discovery_log = setup_logger("discovery", logging.INFO)
        threading.Thread(
            target=responder.start,
            daemon=True,
            name="DiscoveryThread"
        ).start()
        discovery_log.info("Discovery responder started")
    else:
        log.warning("Discovery responder skipped as it was previously completed")

    # Start HTTP API server on port 80
    api_log = setup_logger("api_http", logging.INFO)
    api_server_80 = VerboseAPIServer(port=80, settings=settings)
    threading.Thread(target=api_server_80.start, daemon=True).start()
    api_log.info("HTTP API server started on port 80")

    # Start HTTPS API server on port 443 with SSL enabled
    api_ssl_log = setup_logger("api_https", logging.INFO)
    api_server_443 = VerboseAPIServer(port=443, use_ssl=True, settings=settings)
    threading.Thread(target=api_server_443.start, daemon=True).start()
    api_ssl_log.info("HTTPS API server started on port 443")

    # Keep main thread alive
    threading.Event().wait()

if __name__ == "__main__":
    main()
