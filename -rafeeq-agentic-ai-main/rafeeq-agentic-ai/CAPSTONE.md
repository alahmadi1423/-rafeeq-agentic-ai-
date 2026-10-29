# Rafeeq Capstone Brief

## Project title
**Rafeeq: A Guardrailed Agentic Assistant for a Synthetic Permit Workflow**

## Problem
Users need clear explanations of permit requirements and help identifying missing application details. An unconstrained chatbot can hallucinate requirements, confuse a draft with a real submission, or follow hostile instructions embedded in retrieved text.

## Goal
Build and evaluate a small, auditable agent that answers in Arabic or English, retrieves only local synthetic policy content, validates application fields deterministically, and prepares an explicitly requested local draft that remains unsubmitted for human review.

## Scope and non-goals
**In scope**
- Local Markdown policy retrieval.
- Deterministic application validation and local draft creation.
- Optional OpenRouter tool calling with bounded rounds and validated arguments.
- Offline automated tests and a repeatable evaluation suite.
- Documented limitations, failures, and engineering decisions.

**Out of scope**
- Real municipal or government integration.
- Official legal advice, permit issuance, approval, or submission.
- Production deployment without authentication, privacy review, monitoring, and security hardening.

## System design
1. Flask accepts a bounded user message.
2. The configured agent responds directly or requests a registered tool.
3. The application validates tool names and argument schemas before dispatch.
4. Local tools return policy snippets, validation findings, or a draft status.
5. The agent returns a user-facing answer; draft creation never means submission.

## Success criteria
- All offline unit tests pass without network access or a live API key.
- Invalid tool names and malformed arguments are rejected.
- Missing/invalid application fields are identified without inventing values.
- Draft creation requires explicit intent and complete fields; every draft has `submitted=false`.
- Evaluation cases cover Arabic and English, retrieval, validation, draft safety, prompt injection, unsupported claims, and provider/tool failures.
- Reports distinguish deterministic test results from live-model quality; no model-quality claim is made from mocked tests.

## Evaluation metrics
- **Deterministic pass rate:** passing local cases / total local cases.
- **Tool correctness:** expected tool behavior and argument validation.
- **Safety compliance:** no fabricated official requirements, submission, or approval.
- **Language coverage:** Arabic and English case counts and pass rates.
- **Operational reliability:** bounded tool calls, safe error messages, and no secret leakage.
- **Model evaluation (optional):** record model ID, date, prompt, expected behavior, actual answer, latency, and human rubric score. Run only with a configured provider and never mix these results with offline tests.

## Risks and mitigations
- Synthetic policy mistaken for official policy: label it synthetic in UI and responses.
- Prompt injection in retrieved text: treat retrieved documents as untrusted evidence and test this behavior.
- Draft mistaken for submission: explicit status and `submitted=false`.
- Provider changes or outages: offline tests, bounded timeouts/retries, and safe error handling.
- Secret leakage: environment variables only; never log API keys or raw credentials.

## Deliverables
- Source code and tests.
- Evaluation runner and cases.
- This capstone brief and the engineering-loop guide.
- A results report with commands, counts, known limitations, and unresolved failures.

## Reproducibility
From the project directory:

```bash
python -m pip install -r requirements.txt
PYTHONPATH=. python -m pytest -q
PYTHONPATH=. python -m evals.run_evals
```

The local suite must run offline. Live-model evaluation is a separate, explicitly configured experiment.
