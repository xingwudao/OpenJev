import asyncio
import http.client
import json
import subprocess
import threading
import unittest
from pathlib import Path

from openjev import AsyncOpenJevClient, OpenJevClient, OpenJevError
from server.__main__ import MAX_BODY, make_server
from server.runtime import Runtime
from test_runtime import FIXTURE


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server(port=0)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        try:
            conn.request(method, path, body, headers or {})
            response = conn.getresponse()
            return response.status, json.loads(response.read())
        finally:
            conn.close()

    def test_metadata(self):
        self.assertEqual(self.request("GET", "/health"),
                         (200, {"status": "ok", "model": "openjev-mock"}))
        self.assertEqual(self.request("GET", "/v1/models")[1]["models"][0],
                         {"id": "openjev-mock", "mock": True})
        self.assertEqual(self.request("GET", "/missing")[0], 404)

    def test_http_errors(self):
        headers = {"Content-Type": "application/json"}
        for body in [b"{", b"\xff", b'{"state": NaN}', b'{"state": 1e999}']:
            self.assertEqual(self.request("POST", "/v1/system_one", body, headers)[0], 400)
        self.assertEqual(self.request("POST", "/v1/system_one", "{}", headers)[0], 422)
        self.assertEqual(self.request("POST", "/v1/system_one", "{}")[0], 415)
        self.assertEqual(self.request("POST", "/missing", "{}", headers)[0], 404)
        self.assertEqual(self.request("POST", "/v1/system_one", "", {
            **headers, "Content-Length": str(MAX_BODY + 1)})[0], 413)
        self.assertEqual(self.request("POST", "/v1/system_one", "", {
            **headers, "Content-Length": "-1"})[0], 400)
        self.assertEqual(self.request("POST", "/v1/system_one", "", {
            **headers, "Transfer-Encoding": "chunked"})[0], 400)

    def test_python_clients(self):
        expected = Runtime().system_one(FIXTURE)
        self.assertEqual(OpenJevClient(self.url + "/").system_one(**FIXTURE), expected)
        actual = asyncio.run(AsyncOpenJevClient(self.url).system_one(**FIXTURE))
        self.assertEqual(actual, expected)
        with self.assertRaises(OpenJevError) as caught:
            OpenJevClient(self.url).system_one(**FIXTURE, model="missing")
        self.assertEqual((caught.exception.status, caught.exception.code), (404, "model_not_found"))

    def test_javascript_client(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(["node", "examples/ticket.mjs", self.url], cwd=root,
                                capture_output=True, text=True, timeout=15, check=True)
        self.assertEqual(json.loads(result.stdout), Runtime().system_one(FIXTURE))

    def test_backend_failure_is_500(self):
        class BrokenBackend:
            model = "openjev-mock"

            def answer(self, state, question):
                raise ValueError("private backend details")

        server = make_server(port=0, runtime=Runtime(BrokenBackend()))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with self.assertLogs(level="ERROR"), self.assertRaises(OpenJevError) as caught:
                OpenJevClient(f"http://127.0.0.1:{server.server_port}").system_one(**FIXTURE)
            self.assertEqual(caught.exception.status, 500)
            self.assertNotIn("private", str(caught.exception))
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
