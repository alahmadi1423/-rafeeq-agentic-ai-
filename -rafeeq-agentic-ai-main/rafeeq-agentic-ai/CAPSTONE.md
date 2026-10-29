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
1. Flask accepts a bounded chat message or structured application payload.
2. The chat agent responds directly or requests a registered tool.
3. The application validates tool names and argument schemas before dispatch.
4. Local policy retrieval returns snippets from the synthetic policy document.
5. Deterministic application endpoints validate allowed fields and required values independently of the LLM.
6. The guided `/application` page lets users validate a form, preview a local draft, and export it as JSON.
7. Draft creation never means submission; exported drafts retain an explicit `submitted=false` status.

## User-facing workflow
1. Open the chat page to ask a policy question, or navigate to `/application` to use the structured form.
2. Enter synthetic demo details only; do not enter real personal data.
3. Call `POST /api/application/validate` to receive field-completeness results.
4. Call `POST /api/application/draft` to create a local draft only when all required fields are valid.
5. Review the preview and optionally download the JSON draft.
6. Treat the result as a demonstration artifact: it is not submitted to a municipality, and no permit is issued.

## API contract
- `POST /api/application/validate`: accepts a JSON object containing only the required string fields; returns deterministic validation results.
- `POST /api/application/draft`: accepts the same field contract; returns an unsubmitted draft when valid and a validation response when incomplete.
- Unexpected fields and non-string values are rejected. The API does not accept a client-supplied approval or submission flag as authority.

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
- Source code for the Flask application, rule-based agent, and optional OpenRouter tool-calling agent.
- Local synthetic policy retrieval and deterministic application validation.
- Guided application-builder UI with local JSON draft export.
- Unit/API tests and deterministic evaluation runner.
- Live-model evaluation plan and manual review rubric (live-model quality is not established until outputs are reviewed).
- This capstone brief and the engineering-loop guide.
- A results report with commands, actual test/evaluation counts, known limitations, and unresolved failures.

## Acceptance checklist
- [ ] The home page and `/application` page load.
- [ ] Valid application fields can be checked and produce a local draft.
- [ ] Missing fields prevent a completed draft.
- [ ] Unexpected JSON fields and non-string values are rejected.
- [ ] Exported JSON clearly indicates the draft is not submitted.
- [ ] Chat and application endpoints return safe errors for invalid input or provider failures.
- [ ] All automated tests and offline evaluations pass in the target environment.
- [ ] The final demo states that all policy and permit data are fictional.
- [ ] No live-model quality claims are made without reviewing actual outputs.

## Reproducibility
From the project directory:

```bash
python -m pip install -r requirements.txt
PYTHONPATH=. python -m pytest -q
PYTHONPATH=. python -m evals.run_evals
```

The local suite must run offline. Live-model evaluation is a separate, explicitly configured experiment.
