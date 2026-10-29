# Test and Evaluation Notes

## Offline tests

Run from the project root:

```bash
python -m pip install -r requirements.txt
PYTHONPATH=. python -m pytest -q
PYTHONPATH=. python -m evals.run_evals
```

The unit tests and deterministic eval runner are designed to run without OpenRouter credentials or network calls. The eval runner checks local policy search, malformed/unknown tool calls, application validation, and the invariant that a draft is never submitted.

## Live-model evaluation

See [evals/MODEL_EVALS.md](evals/MODEL_EVALS.md) for Arabic and English scenarios, prompt-injection checks, unsupported-claim checks, a scoring rubric, and a reporting template. Live-model outputs must be evaluated separately and must record the model ID and date. Do not treat mocked, rule-based, or local-tool tests as evidence of live-model answer quality.

## Engineering workflow

Follow [ENGINEERING_LOOP.md](ENGINEERING_LOOP.md): reproduce a failure, specify expected behavior, add a regression test, make a focused change, run the full offline suite and evals, review safety behavior, and document the result.

## Evaluation limitations

The current deterministic cases are a small smoke-test set, not a statistically representative benchmark. They verify local behavior, not semantic answer quality, and do not prove robustness against every prompt injection. Expand the set whenever a new failure is observed. Never treat the synthetic policy document as an official Saudi regulation.
