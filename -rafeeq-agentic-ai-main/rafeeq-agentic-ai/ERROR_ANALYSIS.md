# Rafeeq Error Analysis

Use this workflow whenever a test, eval, or manual run fails. The goal is to convert each failure into a reproducible test and a focused fix.

## Failure categories

- **Retrieval / grounding:** relevant policy content was missed, or a claim was not supported by the synthetic policy.
- **Intent / tool selection:** the agent selected the wrong tool or answered when a tool was needed.
- **Argument validation:** missing, malformed, unexpected, or non-text tool arguments were accepted or handled poorly.
- **Tool logic:** local validation, policy search, or draft creation returned an incorrect result.
- **Safety:** unknown tools were invoked, prompt injection changed intended behavior, secrets were exposed, or a draft was described as submitted/approved.
- **Provider / infrastructure:** missing API key, rate limit, timeout, invalid model response, or provider outage.
- **UI / API:** request validation, error handling, or interface behavior failed.

## Triage workflow

1. **Capture** the smallest reproducible input and expected result. Remove API keys, personal data, and other secrets.
2. **Classify** the failure using one category above and assign severity.
3. **Locate** the responsible layer (UI/API, agent routing, tool validation, local tool, provider integration, or response generation).
4. **Add a regression test first** so the failure is reproducible without relying on memory or a one-off demo.
5. **Fix narrowly** while preserving existing safety boundaries.
6. **Run the focused test**, then the full test suite and offline evals:
   ```bash
   PYTHONPATH=. python -m pytest -q
   PYTHONPATH=. python -m evals.run_evals
   ```
7. **Compare** the baseline and candidate outcomes. For live-model failures, rerun the same versioned cases and record model ID, date, latency, and token/cost data when available.
8. **Document** the root cause, fix, regression test, and remaining limitations.

## Incident record template

| Field | Record |
|---|---|
| Case ID / language | |
| Expected behavior | |
| Observed behavior | |
| Category / severity | |
| Reproduction steps | |
| Root cause (evidence-based) | |
| Regression test | |
| Fix / commit | |
| Before → after result | |
| Remaining risk | |

## Priority rules

1. Block release for safety invariant violations.
2. Fix high-impact correctness failures and recurring failures.
3. Address robustness and error-message quality.
4. Optimize latency and cost only after correctness and safety remain stable.

Do not report a root cause as confirmed until evidence supports it. Distinguish observations from hypotheses. The local food-truck policy is synthetic and must not be represented as official Saudi municipal policy.
