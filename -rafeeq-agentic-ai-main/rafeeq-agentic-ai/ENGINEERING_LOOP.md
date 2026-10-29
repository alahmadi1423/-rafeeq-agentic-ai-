# Rafeeq Engineering Loop

Use this loop for every meaningful change. The goal is to make improvements measurable rather than relying on a few successful demos.

## Loop

1. **Observe** — reproduce a failure or identify a user-facing risk. Save a minimal Arabic or English example without secrets or personal data.
2. **Specify** — write the expected behavior and a regression test before changing implementation.
3. **Change** — make the smallest focused code change; keep tool boundaries and human-approval safeguards intact.
4. **Verify quickly** — run the relevant unit tests and static checks available in the project.
5. **Evaluate broadly** — run the full offline test suite and deterministic eval set.
6. **Review traces** — inspect tool choice, tool status, failure paths, and whether the response made unsupported claims. Do not log API keys or sensitive inputs.
7. **Compare** — record before/after pass counts, newly failing cases, and any latency/model configuration changes.
8. **Decide** — accept, revise, or revert. Do not ship a change that weakens a safety invariant just to improve answer fluency.
9. **Document** — update the README/evaluation notes with what changed, how it was tested, and known limitations.

## Required release gates

- [ ] Offline tests pass.
- [ ] Eval runner exits non-zero if any case fails.
- [ ] Tool arguments are validated before dispatch.
- [ ] No draft is reported as submitted or approved.
- [ ] Retrieved policy content is treated as untrusted evidence.
- [ ] Error responses do not expose exception details or credentials.
- [ ] Arabic and English cases are represented.
- [ ] Test results state the dataset size and do not imply live-model quality when no live model was called.

## Failure triage
Classify each failure as retrieval, intent/tool selection, argument validation, tool logic, response grounding, safety, provider/infrastructure, or UI/API. Add a regression case first, then fix the narrowest responsible layer.

## Suggested cadence
For a small project, run the focused test after each change, the complete suite before each commit, and the full eval set before demos or releases. Run live-model evaluations separately because provider responses can vary and may incur cost.
