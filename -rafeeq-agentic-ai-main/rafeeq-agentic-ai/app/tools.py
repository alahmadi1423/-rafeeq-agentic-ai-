from pathlib import Path
from typing import Any

from app.rag import retrieve_chunks

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
    """Retrieve ranked, source-cited chunks from local policies and uploaded PDFs."""
    result = retrieve_chunks(query)
    if not result.get("ok"):
        return {"ok": False, "error": result.get("error", "Policy search failed."), "results": []}
    return {
        "ok": True,
        "query": query,
        "results": result["results"],
        "retrieval": result["retrieval"],
        "synthetic": result["synthetic"],
    }


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
