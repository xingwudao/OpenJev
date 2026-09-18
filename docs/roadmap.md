# Roadmap

## Phase 0: Repository Skeleton

- README and project positioning.
- Directory structure.
- Initial JSON schema for the protocol.

## Phase 1: Contract Package

Status: implemented with request/response schemas and runtime semantic checks.

- Harden `specs/system-one.schema.json`.
- Add contract tests.
- Add example request and response fixtures.

## Phase 2: Mock Runtime

Status: implemented with local HTTP transport and Python/JavaScript clients.

- Add deterministic mock answers.
- Add a small local HTTP server.
- Add JavaScript and Python SDK calls against the mock server.

## Phase 3: Backend Adapters

- Add an adapter interface.
- Add one open-model adapter.
- Add one LLM structured-output adapter for baseline comparison.

## Phase 4: Evaluation

- Add calibration metrics.
- Add workflow-level eval fixtures.
- Track confidence thresholds and abstention behavior.
