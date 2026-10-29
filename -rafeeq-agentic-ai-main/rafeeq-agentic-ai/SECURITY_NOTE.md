# Security Notes — Rafeeq (Educational Prototype)

## Implemented safeguards

- Only three registered tools are callable by the OpenRouter agent.
- User messages, policy queries, and application text have explicit length limits.
- Tool output is treated as untrusted context in the system instructions.
- Tool exceptions returned to the model are sanitized; detailed failures should remain in server logs.
- Draft creation copies only the four allowlisted application fields and never marks a draft as submitted.
- The Flask endpoint validates JSON and message shape and applies a lightweight per-process rate limit.
- The UI displays a trace of the tool names and coarse outcome status when the agent returns one.

## Threats not solved

- This prototype has no user authentication, persistent audit log, or persistent rate-limit store.
- A process-local rate limiter can be bypassed by restarting the app or distributing requests across workers.
- Prompt instructions are defense-in-depth, not a security boundary. Enforcement must remain in code.
- No real municipal database, permit submission, email, payment, or booking integration exists.
- Do not use real applicant data or expose the development server publicly.
- No claim is made that the model's natural-language answers are always factually correct.

## Before production

1. Add authentication and authorization, plus CSRF protection if cookie sessions are introduced.
2. Store approvals and audit events durably; bind approvals to a specific user, draft, and action payload.
3. Use a shared rate limiter, reverse-proxy request limits, timeouts, and monitoring.
4. Add red-team tests for direct/indirect prompt injection, data leakage, false approval claims, and tool argument abuse.
5. Run model-based evaluations with a real key and review failed cases before reporting quality metrics.
