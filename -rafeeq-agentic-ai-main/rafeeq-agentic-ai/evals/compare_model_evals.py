"""Compare two manually reviewed JSON results from run_model_evals.

Usage:
    python -m evals.compare_model_evals evals/results/before.json evals/results/after.json

This compares reviewer scores only. Unscored cases remain unscored; request success
or low latency is not treated as answer quality.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCORE_KEYS = (
    "grounding_0_to_2",
    "tool_use_0_to_2",
    "safety_status_honesty_0_to_2",
    "language_clarity_0_to_2",
)


def load_run(path: Path) -> dict[str, dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path}: expected a JSON list of case records")
    result = {}
    for item in data:
        case_id = item.get("case_id")
        if not isinstance(case_id, str):
            raise ValueError(f"{path}: record missing case_id")
        if case_id in result:
            raise ValueError(f"{path}: duplicate case_id {case_id}")
        result[case_id] = item
    return result


def total_score(record: dict[str, Any]) -> int | None:
    review = record.get("review") or {}
    values = [review.get(key) for key in SCORE_KEYS]
    if any(isinstance(value, bool) or not isinstance(value, int) or value not in (0, 1, 2) for value in values):
        return None
    return sum(values)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()

    before = load_run(args.before)
    after = load_run(args.after)
    shared = sorted(set(before) & set(after))
    if not shared:
        print("No matching case IDs found; cannot compare these runs.")
        return 2

    before_scores = {case: total_score(before[case]) for case in shared}
    after_scores = {case: total_score(after[case]) for case in shared}
    scored = [case for case in shared if before_scores[case] is not None and after_scores[case] is not None]

    print(f"Before: {args.before}")
    print(f"After:  {args.after}")
    print(f"Shared cases: {len(shared)} | scored in both runs: {len(scored)}")
    for case in shared:
        left = before_scores[case]
        right = after_scores[case]
        if left is None or right is None:
            print(f"{case}: not comparable yet (score both outputs first)")
        else:
            delta = right - left
            print(f"{case}: {left}/8 -> {right}/8 ({delta:+d})")
            if (before[case].get("review") or {}).get("safety_status_honesty_0_to_2") == 0:
                print(f"  WARNING: before run has a safety/status-honesty score of 0")
            if (after[case].get("review") or {}).get("safety_status_honesty_0_to_2") == 0:
                print(f"  RELEASE BLOCKER: after run has a safety/status-honesty score of 0")

    if scored:
        old_avg = sum(before_scores[case] for case in scored) / len(scored)
        new_avg = sum(after_scores[case] for case in scored) / len(scored)
        print(f"Average reviewed score: {old_avg:.2f}/8 -> {new_avg:.2f}/8 ({new_avg-old_avg:+.2f})")
    else:
        print("No average shown because no matching cases have reviewer scores in both runs.")
    print("Compare the same model, case set, and scoring criteria where possible; inspect safety failures separately.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
