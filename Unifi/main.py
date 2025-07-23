from camera_data.camera_settings import CameraSettings
from discovery_responder import DiscoveryResponder
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json

# ---- HTTPS API Logging Server ----
class VerboseAPIHandler(BaseHTTPRequestHandler):
    def log_request_info(self):
        print("\n" + "="*60)
        print(f"[{self.command}] {self.client_address[0]}:{self.client_address[1]} {self.path}")
        print("Headers:")
        for k, v in self.headers.items():
            print(f"  {k}: {v}")
        if self.command in ["POST", "PUT"]:
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                print("JSON Body:")
                print(json.dumps(json.loads(body), indent=2))
            except:
                print("Raw Body:")
                print(body.decode(errors='replace'))

    def do_GET(self):
        self.log_request_info()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_POST(self):
        self.log_request_info()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

    def do_PUT(self):
        self.do_POST()

    def do_DELETE(self):
        self.log_request_info()
        self.send_response(204)
        self.end_headers()

def run_http_server(port):
    def _thread():
        server = HTTPServer(("0.0.0.0", port), VerboseAPIHandler)
        print(f"[+] HTTP API server running on port {port}")
        server.serve_forever()
    threading.Thread(target=_thread, daemon=True).start()

# ---- Main Entrypoint ----
if __name__ == "__main__":
    settings = CameraSettings()

    MAC = settings.mac_bytes
    IP = settings.ip_bytes
    PRIMARY_ADDRESS = MAC + IP

    responder = DiscoveryResponder(settings)
    responder.start()

    # HTTP port
    run_http_server(80)

    # Keep the main thread alive
    threading.Event().wait()
