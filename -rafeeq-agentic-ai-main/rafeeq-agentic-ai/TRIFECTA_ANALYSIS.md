# Rafeeq Trifecta Analysis

This document defines a practical evaluation framework for the Rafeeq agent. It is a measurement plan, not a claim that benchmark results have already been collected.

## The three dimensions

Evaluate these dimensions together because optimizing one in isolation can hide regressions in another.

| Dimension | What to measure | How to report |
|---|---|---|
| **Quality** | Task success, policy-grounded correctness, correct tool selection, valid tool arguments, and unsupported claims | Overall pass rate and per-category pass rate |
| **Latency** | End-to-end response time and, where available, model/provider time | Median (p50) and p95 latency, measured over the same cases |
| **Cost** | Model input/output tokens and estimated provider cost per completed task | Average cost per case and cost per successful task |

**Safety is a hard release gate**, not a metric to trade away for speed or lower cost. Preserve the invariants that unknown tools are blocked, invalid arguments are rejected, synthetic policy is not presented as official regulation, and drafts are never described as submitted or approved.

## Evaluation protocol

1. Freeze a versioned set of Arabic and English test cases.
2. Record the model identifier, date, prompt/configuration version, and provider settings.
3. Run the same cases against the baseline and candidate version.
4. Capture pass/fail, failure category, latency, token usage, and cost when available.
5. Compare quality, p50/p95 latency, and cost together.
6. Inspect regressions and representative failures before accepting the change.
7. Publish the sample size and limitations. Do not infer live-model quality from mocked or offline tool tests.

## Decision table

| Outcome | Decision |
|---|---|
| Quality improves or stays stable, latency/cost improve, safety gates pass | Candidate may be accepted after review |
| Quality drops, even if faster or cheaper | Investigate and normally reject |
| Safety invariant fails | Block release and add a regression test |
| Latency/cost data unavailable | Mark as **not measured**; do not estimate or invent values |
| Too few cases or unstable results | Expand the dataset and rerun before making strong claims |

## Error analysis

For every failed case, record:
- Case ID and language (avoid personal or sensitive data).
- Expected behavior versus observed behavior.
- Failure category: retrieval/grounding, intent or tool selection, argument validation, tool logic, safety, provider/infrastructure, or UI/API.
- Severity and reproducibility.
- Root-cause hypothesis supported by evidence.
- Regression test added and the change made.
- Baseline versus post-fix outcome.

Prioritize safety failures first, then repeated/high-impact correctness failures, then latency and cost optimizations. A successful fix should reduce the target failure without causing new regressions in the full eval suite.

## Results template

Use this table after a real run; leave uncollected values blank or mark them not measured.

| Version/model | Cases | Pass rate | p50 latency | p95 latency | Avg. cost/task | Safety failures |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | Not measured | Not measured | Not measured | Not measured | Not measured | Not measured |
| Candidate | Not measured | Not measured | Not measured | Not measured | Not measured | Not measured |

## Limitations

- The existing offline eval runner checks deterministic local-tool behavior; it does not measure live model answer quality.
- Cost depends on model pricing, token usage, and provider routing; record the source and date for any pricing calculation.
- Latency varies by provider and network conditions; compare runs under similar conditions.
- The project's food-truck policy is synthetic and must never be presented as official Saudi municipal policy.
