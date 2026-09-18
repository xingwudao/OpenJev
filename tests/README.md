# Tests

Install root requirements and the local Python SDK, then run from the repo root:

```sh
.venv/bin/python -m unittest discover -s tests -v
npm --prefix sdk/js test
```

Python tests cover request/response contracts, probability invariants, backend
failures, HTTP errors, determinism, and both SDKs against a real local server.
They require Node.js and start servers on ephemeral ports, closing them on exit.
JavaScript tests cover helpers, HTTP error handling, and timeout behavior.

Type checks:

```sh
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m mypy sdk/python/openjev
npm --prefix sdk/js ci
npm --prefix sdk/js run typecheck
```
