# OpenJev Python SDK

Install locally with `python -m pip install -e sdk/python` from the repo root.
Requires Python 3.11+; no runtime dependencies.

```python
from openjev import Noul, OpenJevClient

client = OpenJevClient()
result = client.system_one(
    state="The payment integration is failing.",
    questions={"urgent": Noul(type="noul", instructions="This requires urgent action.")},
)
print(result["answers"]["urgent"])
```

`Choice`, `Score`, and `Noul` are TypedDict question definitions. Validation
occurs on the server. `AsyncOpenJevClient` exposes the same call with `await`.
`OpenJevError` exposes HTTP `status` and protocol `code`.
Set `base_url` and `timeout` (seconds) on the client constructor.
