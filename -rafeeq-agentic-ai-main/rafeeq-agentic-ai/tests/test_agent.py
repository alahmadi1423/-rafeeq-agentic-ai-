from app.agent import run_agent


def test_agent_routes_policy_question():
    result = run_agent("ما متطلبات تصريح عربة طعام؟")
    assert result["tool"] == "search_policies"
    assert result["ok"] is True


def test_agent_rejects_empty_message():
    result = run_agent("   ")
    assert result["ok"] is False


def test_agent_requires_application_data():
    result = run_agent("تحقق من الطلب")
    assert result["ok"] is False
    assert result["tool"] == "validate_application"


def test_agent_draft_waits_for_approval():
    application = {
        "applicant_name": "Demo User",
        "location": "Demo Location",
        "activity": "Food truck",
        "contact": "demo@example.com",
    }

    result = run_agent("جهز مسودة الطلب", application)

    assert result["tool"] == "create_application_draft"
    assert result["result"]["status"] == "awaiting_approval"
    assert result["result"]["submitted"] is False


def test_explicit_draft_intent_is_not_misrouted_to_policy_search():
    application = {
        "applicant_name": "Demo User",
        "location": "Demo Location",
        "activity": "Coffee",
        "contact": "demo@example.com",
    }
    result = run_agent("أنشئ مسودة تصريح لعربة طعام", application)
    assert result["tool"] == "create_application_draft"
    assert result["result"]["status"] == "awaiting_approval"


def test_unknown_agent_request_does_not_call_a_tool():
    result = run_agent("مرحبا، كيف حالك؟")
    assert result["tool"] is None
