"""Schema-validated System One runtime and deterministic mock backend."""

import hashlib
import json
import math
from pathlib import Path
from typing import Protocol

from jsonschema import Draft202012Validator

SPECS = Path(__file__).resolve().parents[1] / "specs"


def validator(filename):
    schema = json.loads((SPECS / filename).read_text())
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


REQUEST = validator("system-one.schema.json")
RESPONSE = validator("system-one-response.schema.json")


class APIError(Exception):
    def __init__(self, status, code, message):
        super().__init__(message)
        self.status = status
        self.code = code


class Backend(Protocol):
    model: str

    def answer(self, state: object, question: dict) -> dict: ...


class MockBackend:
    model = "openjev-mock"

    def answer(self, state, question):
        # Hash each question independently so batching cannot change its answer.
        seed = json.dumps([state, question], sort_keys=True, ensure_ascii=True,
                          separators=(",", ":"), allow_nan=False)

        def weight(label):
            digest = hashlib.sha256((seed + "\n" + label).encode()).digest()
            return int.from_bytes(digest[:4], "big") + 1

        kind = question["type"]
        if kind == "noul":
            yes, no = weight("yes"), weight("no")
            return {"type": kind, "noul": yes / (yes + no)}
        criteria = question["criteria"]
        labels = sorted(criteria) if kind == "choice" else [str(i) for i in range(len(criteria))]
        weights = {label: weight(label) for label in labels}
        total = sum(weights.values())
        probabilities = {label: value / total for label, value in weights.items()}
        ordered = sorted(probabilities.values(), reverse=True)
        result = {"type": kind, "probabilities": probabilities,
                  "confidence": ordered[0] - ordered[1]}
        if kind == "choice":
            result["choice"] = max(probabilities, key=probabilities.get)
        else:
            result["score"] = sum(int(k) * p for k, p in probabilities.items())
            result["legend"] = dict(zip(labels, criteria))
        return result


def validate_answers(request, response):
    RESPONSE.validate(response)
    if response["answers"].keys() != request["questions"].keys():
        raise ValueError("Answer IDs do not match question IDs")
    for key, question in request["questions"].items():
        answer = response["answers"][key]
        if answer["type"] != question["type"]:
            raise ValueError("Answer type does not match question type")
        if answer["type"] == "noul":
            if not math.isfinite(answer["noul"]):
                raise ValueError("Non-finite probability")
            continue
        probabilities = answer["probabilities"]
        labels = (set(question["criteria"]) if answer["type"] == "choice"
                  else {str(i) for i in range(len(question["criteria"]))})
        if probabilities.keys() != labels or not math.isclose(sum(probabilities.values()), 1, abs_tol=1e-9):
            raise ValueError("Invalid probability distribution")
        if not all(math.isfinite(p) for p in probabilities.values()):
            raise ValueError("Non-finite probability")
        ranked = sorted(probabilities.values(), reverse=True)
        if not math.isclose(answer["confidence"], ranked[0] - ranked[1], abs_tol=1e-9):
            raise ValueError("Invalid confidence margin")
        if answer["type"] == "choice":
            if probabilities.get(answer["choice"]) != max(probabilities.values()):
                raise ValueError("Choice is not a maximum-probability option")
        else:
            expected = sum(int(k) * p for k, p in probabilities.items())
            legend = {str(i): c for i, c in enumerate(question["criteria"])}
            if answer["legend"] != legend or not math.isclose(answer["score"], expected, abs_tol=1e-9):
                raise ValueError("Invalid score or legend")


class Runtime:
    def __init__(self, backend: Backend | None = None):
        self.backend = backend or MockBackend()

    def system_one(self, request):
        error = next(REQUEST.iter_errors(request), None)
        if error:
            path = "/".join(map(str, error.absolute_path)) or "$"
            raise APIError(422, "invalid_request", f"Invalid request at {path}")
        model = request.get("model", self.backend.model)
        if model != self.backend.model:
            raise APIError(404, "model_not_found", f"Unknown model: {model}")
        response = {
            "model": model,
            "answers": {key: self.backend.answer(request["state"], q)
                        for key, q in request["questions"].items()},
            "usage": {"input_tokens": 0, "output_tokens": 0},
        }
        validate_answers(request, response)
        return response
