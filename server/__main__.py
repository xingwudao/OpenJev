"""Local HTTP transport. Run with python -m server."""

import argparse
import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .runtime import APIError, Runtime

MAX_BODY = 1024 * 1024


def reject_constant(value):
    raise ValueError(f"Invalid JSON number: {value}")


def make_server(host="127.0.0.1", port=8000, runtime=None):
    runtime = runtime or Runtime()

    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(10)

        def log_message(self, format, *args):
            pass

        def send_json(self, status, value):
            body = json.dumps(value, allow_nan=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def failure(self, error):
            self.send_json(error.status, {"error": {"code": error.code, "message": str(error)}})

        def do_GET(self):
            if self.path == "/health":
                self.send_json(200, {"status": "ok", "model": runtime.backend.model})
            elif self.path == "/v1/models":
                self.send_json(200, {"models": [{"id": runtime.backend.model, "mock": True}]})
            else:
                self.failure(APIError(404, "not_found", "Route not found"))

        def do_POST(self):
            try:
                if self.path != "/v1/system_one":
                    raise APIError(404, "not_found", "Route not found")
                if self.headers.get_content_type() != "application/json":
                    raise APIError(415, "unsupported_media_type", "Use application/json")
                if self.headers.get("Transfer-Encoding"):
                    raise APIError(400, "invalid_request", "Transfer-Encoding is not supported")
                sizes = self.headers.get_all("Content-Length", [])
                if not sizes:
                    raise APIError(411, "length_required", "Content-Length is required")
                if len(sizes) != 1 or not sizes[0].isascii() or not sizes[0].isdigit():
                    raise APIError(400, "invalid_request", "Invalid Content-Length")
                size = int(sizes[0])
                if size > MAX_BODY:
                    raise APIError(413, "request_too_large", "Body limit is 1 MiB")
                raw = self.rfile.read(size)
                if len(raw) != size:
                    raise APIError(400, "invalid_json", "Incomplete body")
                request = json.loads(raw.decode("utf-8"), parse_constant=reject_constant)
                # Also reject finite JSON literals that overflow a Python float.
                json.dumps(request, allow_nan=False)
            except APIError as error:
                self.failure(error)
                return
            except (ValueError, UnicodeError, RecursionError):
                self.failure(APIError(400, "invalid_json", "Invalid JSON request"))
                return
            except TimeoutError:
                self.failure(APIError(408, "request_timeout", "Request body timed out"))
                return
            try:
                result = runtime.system_one(request)
            except APIError as error:
                self.failure(error)
                return
            except Exception:
                logging.exception("System One request failed")
                self.failure(APIError(500, "internal_error", "Backend failed"))
                return
            self.send_json(200, result)

    return ThreadingHTTPServer((host, port), Handler)


def main():
    parser = argparse.ArgumentParser(description="OpenJev local mock API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    with make_server(args.host, args.port) as server:
        print(f"OpenJev mock API: http://{args.host}:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
