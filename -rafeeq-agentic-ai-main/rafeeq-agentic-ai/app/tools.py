from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
POLICIES_DIR = ROOT_DIR / "policies"
MAX_QUERY_LENGTH = 300
MAX_FIELD_LENGTH = 300
MAX_POLICY_CONTEXT_LENGTH = 6000

FIELD_LABELS = {
    "applicant_name": "اسم المتقدم",
    "location": "الموقع",
    "activity": "النشاط",
    "contact": "معلومات التواصل",
}
REQUIRED_FIELDS = tuple(FIELD_LABELS)


def search_policies(query: str) -> dict[str, Any]:
    """Search local synthetic policy documents with bounded context."""
    if not isinstance(query, str) or not query.strip():
        return {"ok": False, "error": "Search query cannot be empty.", "results": []}
    if len(query) > MAX_QUERY_LENGTH:
        return {"ok": False, "error": "Search query is too long.", "results": []}
    if not POLICIES_DIR.exists():
        return {"ok": False, "error": "Policy directory was not found.", "results": []}

    query_terms = {term for term in query.lower().split() if len(term) > 1}
    results = []
    for path in sorted(POLICIES_DIR.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        lowered = text.lower()
        score = sum(lowered.count(term) for term in query_terms)
        if score:
            results.append({
                "source": path.name,
                "score": score,
                # Retrieved text is untrusted evidence, not agent instructions.
                "content": text[:MAX_POLICY_CONTEXT_LENGTH],
                "truncated": len(text) > MAX_POLICY_CONTEXT_LENGTH,
                "synthetic": True,
            })
    results.sort(key=lambda item: item["score"], reverse=True)
    return {"ok": True, "query": query, "results": results, "synthetic": True}


def validate_application(application: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize the required fields for a demo application."""
    if not isinstance(application, dict):
        return {"valid": False, "missing_fields": list(REQUIRED_FIELDS), "errors": ["Application must be an object."]}

    missing = []
    errors = []
    for field in REQUIRED_FIELDS:
        value = application.get(field, "")
        if not isinstance(value, str):
            errors.append(f"{field} must be text.")
            missing.append(field)
        elif not value.strip():
            missing.append(field)
        elif len(value.strip()) > MAX_FIELD_LENGTH:
            errors.append(f"{field} exceeds the maximum length.")

    return {
        "valid": not missing and not errors,
        "missing_fields": missing,
        "missing_field_labels": [FIELD_LABELS[field] for field in missing],
        "errors": errors,
    }


def create_application_draft(application: dict[str, Any]) -> dict[str, Any]:
    """Create a local draft and stop for explicit human approval."""
    validation = validate_application(application)
    if not validation["valid"]:
        return {
            "status": "incomplete",
            "missing_fields": validation["missing_fields"],
            "missing_field_labels": validation["missing_field_labels"],
            "errors": validation["errors"],
            "submitted": False,
            "synthetic": True,
        }
    safe_draft = {field: application[field].strip() for field in REQUIRED_FIELDS}
    return {
        "status": "awaiting_approval",
        "message": "Draft prepared. Human approval is required before any further action.",
        "draft": safe_draft,
        "submitted": False,
        "synthetic": True,
    }
