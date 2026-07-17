"""Minimal HTTP 200 responder for the Celery worker's Railway service.

The worker process has no HTTP server of its own, but it shares the same
railway.json (and therefore the same /health check) as the web service
since both deploy from this one repo/Dockerfile. This runs alongside the
real Celery worker (see Dockerfile's PROCESS_TYPE branch) purely so
Railway's healthcheck has something to hit — it says nothing about the
worker's actual ability to process tasks.
"""
import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 — dispatched by name from BaseHTTPRequestHandler, can't rename
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
