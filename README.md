# OpenJev

OpenJev is an open-source design for a Jev-like "System One" decision
interface: state goes in, typed probabilistic decisions come out.

The goal of this repository is to make the interface, SDK surface, service
boundary, examples, and evaluation workflow public and hackable before any
model implementation is added.

This project is not affiliated with TypeSafe AI. It does not include TypeSafe's
Jev model, weights, training data, training method, service, or private
benchmarks.

## What Jev Is For

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
  "model": "openjev-local",
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

Expected response shape:

```json
{
  "model": "openjev-local",
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
      "confidence": 0.45
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
- `sdk/js/`: future JavaScript or TypeScript SDK.
- `sdk/python/`: future Python SDK.
- `server/`: future local or hosted API service implementation.
- `examples/`: runnable examples once an implementation exists.
- `evals/`: calibration, regression, and workflow benchmark harnesses.
- `tests/`: contract and behavior tests.

## Project Status

Status: initialized design skeleton.

What exists now:

- README;
- repository directory layout;
- initial System One JSON schema;
- documentation placeholders.

What does not exist yet:

- trained model;
- inference server;
- SDK implementation;
- hosted API;
- benchmark results.

## Roadmap

1. Finalize the `system_one` request and response schema.
2. Add typed SDK interfaces for JavaScript and Python.
3. Implement a deterministic mock backend for examples and tests.
4. Add adapter interfaces for open models and classifier backends.
5. Add calibration metrics and workflow eval fixtures.
6. Publish example applications for ticket routing and guardrails.

## License

No license has been selected yet. Add a license before accepting external
contributions or publishing packages.
