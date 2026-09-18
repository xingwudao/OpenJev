# OpenJev - Jev-Inspired System One Decision API

OpenJev is an independent project inspired by **Jev**, the **System One** model
from **[TypeSafe.ai (TypeSafe AI)](https://typesafe.ai/)**. It implements a
Jev-inspired decision API with `choice`, `score`, and `noul` primitives:
state goes in, typed probabilistic decisions come out.

Explore a local HTTP API, Python SDK, and JavaScript / TypeScript SDK for
prototyping ticket routing, classification, scoring, and AI guardrail workflows.

The first runnable release includes a local mock API, Python and JavaScript
clients, schema validation, and end-to-end tests. Mock probabilities are synthetic:
they do not measure truth, risk, or model quality.

This project is not affiliated with TypeSafe AI. It does not include TypeSafe's
Jev model, weights, training data, training method, service, or private
benchmarks.

中文简介：OpenJev 是受 TypeSafe.ai 的 Jev 模型启发的独立决策 API 项目，
提供本地 mock 服务、Python 和 JavaScript / TypeScript SDK，
用于验证分类、评分、工单路由和 AI 护栏的接口流程。
当前不包含 Jev 模型权重，也不提供真实模型推理。

## Quick Start

Requires Python 3.11+ and Node.js 20+ for JavaScript examples and tests.
Run these commands from the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -e sdk/python
.venv/bin/python -m server --port 8000
```

In another terminal:

```sh
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/v1/system_one \
  -H 'Content-Type: application/json' --data-binary @examples/ticket.json
.venv/bin/python examples/ticket.py
node examples/ticket.mjs
```

The server binds to loopback by default. It is a local development service
without authentication or production serving infrastructure.
Only `openjev-mock` is supported; omit `model` to select it.
See [the protocol](docs/protocol.md) for limits, errors, and probability semantics.

```sh
.venv/bin/python -m unittest discover -s tests -v
npm --prefix sdk/js test
```

## What Is TypeSafe.ai Jev Used For?

Jev, as described by TypeSafe AI, is aimed at machine-native automation instead
of chat. The key idea is:

- provide a shared `state`, usually text or structured JSON;
- ask one or many narrow typed questions about that state;
- receive structured answers that code can branch on directly;
- use probabilities and confidence to decide when to act, review, or abstain.

This is useful for software workflows such as:

- routing support tickets;
- classifying documents;
- scoring risk or severity;
- deciding whether an LLM input or output needs a guardrail;
- ranking candidates from a fixed option set;
- turning natural language requests into ordinary typed function calls.

It is not meant for:

- open-ended chat;
- writing prose;
- code generation;
- long multi-step reasoning in a single prompt;
- any use case where the output space is not known in advance.

## OpenJev Design

OpenJev starts with the contract rather than the model.

The first public surface is a `system_one` call:

```json
{
  "state": {
    "ticket": "Stripe connection has failed for 3 days. We are losing sales."
  },
  "model": "openjev-mock",
  "questions": {
    "department": {
      "type": "choice",
      "instructions": "Which team should handle `ticket`?",
      "criteria": {
        "billing": "Payment, invoice, subscription, or charge issues.",
        "technical": "Bugs, integrations, API, or product failures.",
        "sales": "Pricing, plan, upgrade, or account expansion questions."
      }
    },
    "frustration": {
      "type": "score",
      "instructions": "How frustrated does the customer appear in `ticket`?",
      "criteria": [
        "Calm and factual.",
        "Frustrated but civil.",
        "Very angry or escalated."
      ]
    },
    "urgent": {
      "type": "noul",
      "instructions": "The message conveys urgency or time sensitivity."
    }
  }
}
```

Illustrative response shape (numbers below are not mock fixture outputs):

```json
{
  "model": "openjev-mock",
  "answers": {
    "department": {
      "type": "choice",
      "choice": "technical",
      "probabilities": {
        "billing": 0.09,
        "technical": 0.89,
        "sales": 0.02
      },
      "confidence": 0.8
    },
    "frustration": {
      "type": "score",
      "score": 1.4,
      "legend": {
        "0": "Calm and factual.",
        "1": "Frustrated but civil.",
        "2": "Very angry or escalated."
      },
      "probabilities": {
        "0": 0.05,
        "1": 0.5,
        "2": 0.45
      },
      "confidence": 0.05
    },
    "urgent": {
      "type": "noul",
      "noul": 0.97
    }
  },
  "usage": {
    "input_tokens": 0,
    "output_tokens": 0
  }
}
```

## Primitives

`choice`
- Purpose: choose exactly one option from a closed set.
- Returns: `choice`, `probabilities`, `confidence`.
- Best for: routing, classification, fixed tool selection.

`score`
- Purpose: place the state on an ordered rubric.
- Returns: `score`, `legend`, `probabilities`, `confidence`.
- Best for: severity, quality, risk, priority, fit.

`noul`
- Purpose: estimate the probability that a statement is true.
- Returns: `noul`, a number from `0` to `1`.
- Best for: yes/no signals where the probability itself is useful.

## Architectural Principles

- Keep code in control.
- Ask focused atomic questions.
- Define the output space before inference.
- Batch independent questions against the same state.
- Compose answers in ordinary code.
- Gate autonomous actions with confidence thresholds.
- Route low-confidence or high-stakes cases to review.
- Treat calibration and abstention as product requirements.

## Repository Layout

```text
.
├── docs/
│   ├── architecture.md
│   ├── roadmap.md
│   └── use-cases.md
├── specs/
│   └── system-one.schema.json
├── sdk/
│   ├── js/
│   └── python/
├── server/
├── examples/
├── evals/
└── tests/
```

Directory intent:

- `docs/`: product design notes, architecture, roadmap, and use-case patterns.
- `specs/`: request and response contracts for interoperable implementations.
- `sdk/js/`: JavaScript SDK with inferred TypeScript answer types.
- `sdk/python/`: synchronous and asynchronous Python SDK.
- `server/`: local HTTP service and replaceable backend boundary.
- `examples/`: runnable ticket request and client examples.
- `evals/`: calibration, regression, and workflow benchmark harnesses.
- `tests/`: contract and behavior tests.

## Project Status

Status: contract and mock runtime implemented (roadmap phases 1 and 2).

What exists now:

- Request and response schemas with runtime semantic validation.
- Deterministic mock backend and local HTTP API.
- Python and JavaScript SDK implementations.
- Examples, contract tests, HTTP tests, and SDK tests.

What does not exist yet:

- trained model;
- real inference backend;
- hosted API;
- benchmark results.

## Roadmap

1. Finalize the `system_one` request and response schema.
2. Add typed SDK interfaces for JavaScript and Python.
3. Implement a deterministic mock backend for examples and tests.
4. Add adapter interfaces for open models and classifier backends.
5. Add calibration metrics and workflow eval fixtures.
6. Publish example applications for ticket routing and guardrails.

## Jev and TypeSafe.ai FAQ

### Is OpenJev an official TypeSafe AI project or an open-weight Jev model?

No. OpenJev is independently developed from the publicly described Jev concepts.
TypeSafe.ai has not supplied this repository with Jev model weights, training
data, or proprietary implementation code.

### Can OpenJev replace the TypeSafe.ai Jev API?

The current release supports local integration prototyping with a deterministic
mock backend. It is not a drop-in replacement for the hosted Jev API, and does
not claim wire compatibility or equivalent prediction quality. Real inference
adapters and calibration evaluations are planned in the [roadmap](docs/roadmap.md).

### Where can I learn about the original Jev model and the OpenJev API?

- [TypeSafe.ai](https://typesafe.ai/): the original Jev product.
- [TypeSafe documentation](https://docs.typesafe.ai/introduction): Jev concepts.
- [TypeSafe primitives](https://docs.typesafe.ai/primitives): typed decisions.
- [OpenJev protocol](docs/protocol.md): local endpoints and answer semantics.
- [OpenJev examples](examples/README.md): runnable Python and JavaScript clients.

## License

No license has been selected yet. Add a license before accepting external
contributions or publishing packages.
