# OpenJev Server

From the repository root, install `requirements.txt`, then run:

```sh
.venv/bin/python -m server --host 127.0.0.1 --port 8000
```

`runtime.py` validates requests and responses and dispatches questions to
`MockBackend`. A replacement backend implements `model` and `answer(state,
question)`. Real backend registration is part of roadmap phase 3.

The server is for local development, using Python's standard-library HTTP
transport and `jsonschema` Draft 2020-12 validation. See
[the protocol](../docs/protocol.md) for routes and semantics.
