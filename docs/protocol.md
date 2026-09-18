# Local API Protocol

This is OpenJev's own versioned interface, inspired by the public Jev concepts.
It does not claim wire compatibility with TypeSafe's API.

## Routes

- `GET /health`: status and active model ID.
- `GET /v1/models`: available model metadata, including `mock: true`.
- `POST /v1/system_one`: JSON request to typed JSON response.

Requests must use `Content-Type: application/json` and `Content-Length`.
The body limit is 1 MiB; body reads time out after 10 seconds of inactivity.
Chunked uploads are not supported. The request contains 1-128 questions;
choice and score criteria contain 2-256 options. State is a string, object,
or array. JSON numbers must be finite. Unknown fields are rejected at the
request and question level. Arbitrary fields inside state are allowed.

Schemas live in `specs/system-one.schema.json` and
`specs/system-one-response.schema.json`. The runtime additionally checks
relationships that JSON Schema cannot express: answer IDs and types, criterion
keys, distribution sums, selected options, expected scores, and legends.

## Answer Semantics

- Choice probabilities cover exactly the provided option keys and sum to one.
  The chosen option has maximum probability. Mock ties use lexical key order.
- Score criteria are indexed from zero in their original order. `score` is the
  expectation over these indices, not a rounded class. `legend` preserves all
  rubric descriptions.
- Choice and score `confidence` is the highest probability minus the second
  highest probability. It is a margin, not a calibrated likelihood of correctness.
- `noul` is a probability in `[0, 1]` for the supplied statement.
- Mock usage counters are zero because no model tokens are consumed.

The mock hashes canonical state and question JSON with SHA-256 to generate
positive weights, then normalizes them. Reordering object keys, changing a
question ID, or adding independent questions does not affect an answer.
Changing score criterion order does affect the rubric. Synthetic probabilities
have no semantic meaning and must not drive real workflow decisions.

## Errors

Errors have the shape:

```json
{"error": {"code": "invalid_request", "message": "Invalid request at questions"}}
```

- `400 invalid_json` or `invalid_request`: malformed JSON or transport headers.
- `404 model_not_found` or `not_found`: unsupported model or route.
- `408 request_timeout`: request body read timed out.
- `411 length_required`: missing body length.
- `413 request_too_large`: body exceeds limit.
- `415 unsupported_media_type`: content type is not JSON.
- `422 invalid_request`: request fails the schema.
- `500 internal_error`: backend failed or returned an invalid answer.

SDKs raise `OpenJevError` for HTTP failures with `status` and `code`.
Connection failures and timeouts remain native transport exceptions.
Clients do not retry automatically. JavaScript timeout units are milliseconds;
Python timeout units are seconds. Python async calls use a worker thread;
cancelling the coroutine does not terminate the in-flight HTTP request, which
remains bounded by its transport timeout.

## Sources

- [TypeSafe introduction](https://docs.typesafe.ai/introduction)
- [TypeSafe primitives](https://docs.typesafe.ai/primitives)
- [Python HTTP server](https://docs.python.org/3/library/http.server.html)
- [JSON Schema validation library](https://python-jsonschema.readthedocs.io/en/stable/validate/)
