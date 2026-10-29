# Test and Evaluation Notes

## Local automated tests

Run from the project root:

```bash
python -m pip install -r requirements.txt
PYTHONPATH=. python -m pytest -q
```

The current offline unit tests cover policy lookup, empty/oversized search queries, application field validation, safe draft field allowlisting, human approval state, agent routing, and blank input. They do not call OpenRouter and do not measure model answer quality.

## Suggested next evaluation set

For a defensible capstone evaluation, add Arabic and English cases for:

- Policy questions: uses the policy tool and clearly says the data is synthetic.
- Missing fields: identifies the missing fields without inventing values.
- Draft intent: creates only a local draft and keeps `submitted=false`.
- Prompt injection: ignores instructions embedded in retrieved policy text.
- Unsupported claims: does not invent fees, official regulations, or approval status.
- Tool failure: reports a safe error and does not leak secrets or exception details.

Record expected tool, expected safety behavior, actual result, latency, and model ID for each run. Report pass rate with the dataset size and model configuration; do not treat mock or rule-based tests as proof of model quality.
