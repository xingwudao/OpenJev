import json
import sys
from pathlib import Path

from openjev import OpenJevClient

request = json.loads(Path(__file__).with_suffix(".json").read_text())
client = OpenJevClient(sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000")
print(json.dumps(client.system_one(**request), indent=2))
