"""Dependency-free synchronous and asynchronous OpenJev clients."""

import asyncio
import json
from typing import Literal, NotRequired, TypedDict
from urllib.error import HTTPError
from urllib.request import Request, urlopen


class Choice(TypedDict):
    type: Literal["choice"]
    instructions: str
    criteria: dict[str, str]


class Score(TypedDict):
    type: Literal["score"]
    instructions: str
    criteria: list[str]


class Noul(TypedDict):
    type: Literal["noul"]
    instructions: str
    criteria: NotRequired[str | dict]


Question = Choice | Score | Noul


class ChoiceAnswer(TypedDict):
    type: Literal["choice"]
    choice: str
    probabilities: dict[str, float]
    confidence: float


class ScoreAnswer(TypedDict):
    type: Literal["score"]
    score: float
    legend: dict[str, str]
    probabilities: dict[str, float]
    confidence: float


class NoulAnswer(TypedDict):
    type: Literal["noul"]
    noul: float


class Usage(TypedDict):
    input_tokens: int
    output_tokens: int


class SystemOneResponse(TypedDict):
    model: str
    answers: dict[str, ChoiceAnswer | ScoreAnswer | NoulAnswer]
    usage: Usage


class OpenJevError(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status = status
        self.code = code


class OpenJevClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout: float = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def system_one(self, *, state: str | dict | list,
                   questions: dict[str, Question], model: str | None = None) -> SystemOneResponse:
        payload = {"state": state, "questions": questions}
        if model is not None:
            payload["model"] = model
        request = Request(self.base_url + "/v1/system_one",
                          data=json.dumps(payload, allow_nan=False).encode(),
                          headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.load(response)
        except HTTPError as error:
            with error:
                try:
                    body = json.load(error)
                    detail = body["error"]
                    code, message = detail["code"], detail["message"]
                except (ValueError, KeyError, TypeError):
                    code, message = "http_error", f"HTTP {error.code}"
            raise OpenJevError(error.code, code, message) from error


class AsyncOpenJevClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout: float = 10):
        self._client = OpenJevClient(base_url, timeout)

    async def system_one(self, *, state: str | dict | list,
                         questions: dict[str, Question], model: str | None = None) -> SystemOneResponse:
        return await asyncio.to_thread(self._client.system_one, state=state,
                                       questions=questions, model=model)
