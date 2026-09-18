# Use Cases

## Support Routing

Ask one `choice` question for the target department, one `score` question for
frustration, and one `noul` question for urgency. Route high-confidence answers
automatically and send ambiguous cases to review.

## LLM Guardrails

Ask `noul` questions for jailbreak attempts, data exfiltration, policy
violations, and prompt injection. Combine them with a severity `score` before
allowing, reviewing, or blocking a request.

## Function Selection

Ask a `choice` question over allowed function names. Ask separate `choice` or
`score` questions for arguments with closed vocabularies. Let ordinary typed
code execute only when confidence clears the action threshold.

## Document Classification

Ask one or more `choice` questions for taxonomy placement. For large
taxonomies, use staged classification: choose a broad family first, then ask a
second question over child classes.
