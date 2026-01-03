
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import os

PORT = 8080

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # LIVENESS: "sono vivo?"
        if self.path == "/healthz":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
            return

        # READINESS: "posso ricevere traffico?"
        # Check rete/DNS semplice. Utile per vedere l'effetto NotReady.
        if self.path == "/readyz":
            try:
                socket.gethostbyname("google.com")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"ready")
            except Exception:
                self.send_response(503)
                self.end_headers()
                self.wfile.write(b"not ready")
            return

        # Endpoint normale per test
        if self.path == "/":
            version = os.getenv("APP_VERSION", "unknown")
            pod = socket.gethostname()
            body = f"hello from k8s minimal app - version={version} pod={pod}\n"

            self.send_response(200)
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

if __name__ == "__main__":
    print(f"Starting minimal app on port {PORT}")
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    server.serve_forever()

