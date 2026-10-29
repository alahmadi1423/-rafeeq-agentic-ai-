"""Deterministic offline evals for Rafeeq's local tools.

Run from the project root:
    PYTHONPATH=. python -m evals.run_evals

These checks do not call OpenRouter and do not measure live-model answer quality.
"""
from __future__ import annotations

import json
import sys
from typing import Any

from app.openrouter_agent import _run_tool
from app.tools import search_policies, validate_application

VALID_APPLICATION = {
    "applicant_name": "Demo User",
    "location": "Demo Location",
    "activity": "Food truck",
    "contact": "demo@example.com",
}


def _cases() -> list[dict[str, Any]]:
    return [
        {
            "name": "policy_search_returns_synthetic_marker",
            "run": lambda: search_policies("food truck"),
            "check": lambda r: r.get("ok") is True and r.get("synthetic") is True,
        },
        {
            "name": "empty_policy_query_is_rejected",
            "run": lambda: search_policies("  "),
            "check": lambda r: r.get("ok") is False and r.get("results") == [],
        },
        {
            "name": "unknown_tool_is_blocked",
            "run": lambda: _run_tool("run_shell", {}),
            "check": lambda r: r.get("ok") is False,
        },
        {
            "name": "malformed_application_arguments_are_blocked",
            "run": lambda: _run_tool("validate_application", {"application": {"applicant_name": "Demo User"}}),
            "check": lambda r: r.get("ok") is False,
        },
        {
            "name": "non_text_application_fields_are_blocked",
            "run": lambda: _run_tool("validate_application", {"application": {**VALID_APPLICATION, "location": 123}}),
            "check": lambda r: r.get("ok") is False,
        },
        {
            "name": "missing_required_field_is_reported",
            "run": lambda: validate_application({**VALID_APPLICATION, "contact": "  "}),
            "check": lambda r: r.get("valid") is False and "contact" in r.get("missing_fields", []),
        },
        {
            "name": "valid_draft_remains_unsubmitted",
            "run": lambda: _run_tool("create_application_draft", {"application": VALID_APPLICATION}),
            "check": lambda r: r.get("status") == "awaiting_approval" and r.get("submitted") is False,
        },
        {
            "name": "draft_with_missing_field_is_not_created",
            "run": lambda: _run_tool("create_application_draft", {"application": {**VALID_APPLICATION, "activity": ""}}),
            "check": lambda r: r.get("status") == "incomplete" and r.get("submitted") is False,
        },
    ]


def main() -> int:
    cases = _cases()
    failures = []
    for case in cases:
        try:
            result = case["run"]()
            passed = bool(case["check"](result))
            detail = "" if passed else f" unexpected result={json.dumps(result, ensure_ascii=False, default=str)}"
        except Exception as exc:  # A failed case must be visible, not abort the suite.
            passed = False
            detail = f" raised {type(exc).__name__}: {exc}"
        print(f"{'PASS' if passed else 'FAIL'} {case['name']}{detail}")
        if not passed:
            failures.append(case["name"])

    print(f"\nOffline evals: {len(cases) - len(failures)}/{len(cases)} passed")
    print("Scope: deterministic local-tool behavior only; no live-model quality measured.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
