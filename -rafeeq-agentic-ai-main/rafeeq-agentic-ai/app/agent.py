from typing import Any

from app.tools import (
    search_policies,
    validate_application,
    create_application_draft,
)


def run_agent(
    message: str,
    application: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run a simple rule-based demo agent."""

    if not message or not message.strip():
        return {
            "ok": False,
            "error": "Please enter a question.",
        }

    text = message.strip().lower()

    # Explicit write-intent must be checked before broad policy keywords.
    # Otherwise "draft a food-truck permit" can be misrouted to policy search.
    draft_terms = (
        "create draft", "prepare draft", "جهز مسودة",
        "أنشئ مسودة", "انشئ مسودة", "جهز لي مسودة",
    )
    if any(term in text for term in draft_terms):
        if application is None:
            return {
                "ok": False,
                "tool": "create_application_draft",
                "error": "Please provide application data.",
            }
        result = create_application_draft(application)
        return {"ok": True, "tool": "create_application_draft", "result": result}

    # Route validation requests before broad policy lookup.
    validation_terms = (
        "validate", "check application", "check my application",
        "تحقق", "افحص الطلب", "راجع الطلب",
    )
    if any(term in text for term in validation_terms):
        if application is None:
            return {
                "ok": False,
                "tool": "validate_application",
                "error": "Please provide application data.",
            }
        result = validate_application(application)
        return {"ok": True, "tool": "validate_application", "result": result}

    # Route policy questions to the search tool.
    search_terms = (
        "policy", "requirement", "requirements", "permit", "food truck",
        "search", "سياسة", "متطلبات", "متطلب", "تصريح", "عربة طعام", "ابحث",
    )
    if any(term in text for term in search_terms):
        result = search_policies(message)
        return {"ok": result["ok"], "tool": "search_policies", "result": result}

    return {
        "ok": True,
        "tool": None,
        "message": (
            "I could not determine which tool to use. "
            "Ask about policy requirements, application "
            "validation, or preparing a draft."
        ),
    }
