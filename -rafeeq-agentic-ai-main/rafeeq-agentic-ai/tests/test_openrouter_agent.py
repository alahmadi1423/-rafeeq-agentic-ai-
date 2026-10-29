import pytest

from app.openrouter_agent import _run_tool


VALID_APPLICATION = {
    "applicant_name": "Demo User",
    "location": "Demo Location",
    "activity": "Food truck",
    "contact": "demo@example.com",
}


def test_policy_tool_rejects_missing_arguments():
    result = _run_tool("search_policies", {})
    assert result["ok"] is False


def test_application_tool_rejects_missing_fields():
    result = _run_tool(
        "validate_application",
        {"application": {"applicant_name": "Demo User"}},
    )
    assert result["ok"] is False


def test_application_tool_rejects_non_text_fields():
    application = {**VALID_APPLICATION, "location": 123}
    result = _run_tool("validate_application", {"application": application})
    assert result["ok"] is False


def test_valid_draft_arguments_create_unsubmitted_draft():
    result = _run_tool("create_application_draft", {"application": VALID_APPLICATION})
    assert result["status"] == "awaiting_approval"
    assert result["submitted"] is False


def test_unknown_tool_is_rejected():
    result = _run_tool("run_shell", {})
    assert result["ok"] is False



def test_provider_failure_is_logged_without_exposing_details(monkeypatch, caplog):
    import logging

    import app.openrouter_agent as agent_module

    class BrokenCompletions:
        def create(self, **kwargs):
            raise RuntimeError("provider diagnostic secret")

    class FakeClient:
        def __init__(self, **kwargs):
            self.chat = type("Chat", (), {"completions": BrokenCompletions()})()

    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(agent_module, "OpenAI", FakeClient)

    with caplog.at_level(logging.ERROR, logger="app.openrouter_agent"):
        result = agent_module.run_openrouter_agent("مرحبا")

    assert result["ok"] is False
    assert result["error"] == "تعذر الاتصال بخدمة النموذج. تحقق من الإعدادات ثم حاول مرة أخرى."
    assert "provider diagnostic secret" not in result["error"]
    assert "OpenRouter agent request failed" in caplog.text
    assert "provider diagnostic secret" in caplog.text
