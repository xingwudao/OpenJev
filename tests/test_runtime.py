import copy
import json
import unittest
from pathlib import Path

from jsonschema import ValidationError
from server.runtime import APIError, REQUEST, RESPONSE, Runtime, validate_answers

FIXTURE = json.loads((Path(__file__).resolve().parents[1] / "examples/ticket.json").read_text())


class RuntimeTests(unittest.TestCase):
    def test_contract_and_semantics(self):
        result = Runtime().system_one(FIXTURE)
        RESPONSE.validate(result)
        validate_answers(FIXTURE, result)
        self.assertEqual(result["model"], "openjev-mock")
        self.assertEqual(result["usage"], {"input_tokens": 0, "output_tokens": 0})
        expected = json.loads((Path(__file__).resolve().parents[1] / "examples/ticket.response.json").read_text())
        self.assertEqual(result, expected)

    def test_deterministic_and_batch_independent(self):
        runtime = Runtime()
        original = copy.deepcopy(FIXTURE)
        expected = runtime.system_one(FIXTURE)
        self.assertEqual(runtime.system_one(FIXTURE), expected)
        reordered = json.loads(json.dumps(FIXTURE, sort_keys=True))
        self.assertEqual(runtime.system_one(reordered), expected)
        for key, question in FIXTURE["questions"].items():
            single = runtime.system_one({"state": FIXTURE["state"], "questions": {"renamed": question}})
            self.assertEqual(single["answers"]["renamed"], expected["answers"][key])
        self.assertEqual(FIXTURE, original)

    def test_request_rejections(self):
        invalid = [None, {}, {"state": 1, "questions": FIXTURE["questions"]},
                   {"state": "", "questions": {}}, {**FIXTURE, "unknown": True}]
        questions = [
            {"type": "choice", "instructions": "Pick", "criteria": {"a": "Only"}},
            {"type": "score", "instructions": "Rate", "criteria": ["Only"]},
            {"type": "noul", "instructions": ""},
            {"type": "unknown", "instructions": "Test"},
            {"type": "noul", "instructions": "Test", "extra": True},
        ]
        invalid += [{"state": "test", "questions": {"q": q}} for q in questions]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(APIError) as caught:
                Runtime().system_one(value)
            self.assertEqual(caught.exception.status, 422)

    def test_model_rejection(self):
        with self.assertRaises(APIError) as caught:
            Runtime().system_one({**FIXTURE, "model": "does-not-exist"})
        self.assertEqual(caught.exception.code, "model_not_found")

    def test_state_types(self):
        for state in ["hello", {}, [], {"text": "你好", "nested": [None, True, 2.3]}]:
            request = {**FIXTURE, "state": state}
            REQUEST.validate(request)
            validate_answers(request, Runtime().system_one(request))

    def test_invalid_backend_answers_rejected(self):
        good = Runtime().system_one(FIXTURE)
        mutations = [
            lambda r: r["answers"].pop("urgent"),
            lambda r: r["answers"]["urgent"].update(noul=2),
            lambda r: r["answers"]["urgent"].update(noul=float("nan")),
            lambda r: r["answers"]["severity"].update(score=999),
            lambda r: r["answers"]["severity"].update(legend={"0": "Wrong", "1": "Wrong"}),
            lambda r: r["answers"]["department"].update(choice="missing"),
            lambda r: r["answers"]["department"].update(probabilities={"a": .5, "b": .5}),
            lambda r: r["answers"]["department"].update(confidence=1),
        ]
        for mutate in mutations:
            result = copy.deepcopy(good)
            mutate(result)
            with self.assertRaises((ValidationError, ValueError)):
                validate_answers(FIXTURE, result)


if __name__ == "__main__":
    unittest.main()
