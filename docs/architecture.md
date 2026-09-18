# Architecture

OpenJev is organized around a small stable protocol.

## Boundary

The service boundary is `system_one`:

- input: `state`, `model`, and `questions`;
- output: `answers`, `model`, and `usage`;
- guarantee: answer shapes match the supplied question types.

The model backend is intentionally replaceable. Future implementations can use:

- a deterministic mock backend;
- a local classifier;
- an LLM adapter constrained to the OpenJev schema;
- a purpose-trained decision model.

## Flow

1. Client builds typed questions.
2. Server validates the request schema.
3. Backend evaluates each question against the same state.
4. Server validates answer shapes.
5. Client composes answers into application logic.

## Current Runtime

`server/runtime.py` owns validation and the backend protocol.
`server/__main__.py` exposes local HTTP routes.
`sdk/python/openjev` and `sdk/js` provide clients without runtime dependencies.
JSON Schema is the server's contract source; semantic checks enforce probability
and question/answer relationships. See [protocol details](protocol.md).

## Design Constraints

- Never rely on prose parsing for final application decisions.
- Keep question IDs stable for code, logs, and tests.
- Keep instructions complete because IDs are not semantic enough.
- Keep high-stakes thresholds explicit in code.
- Preserve probability distributions for audit and calibration.
