from app.web_app import app


def test_application_page_loads():
    response = app.test_client().get("/application")

    assert response.status_code == 200
    assert "جهّز طلبك خطوة بخطوة".encode() in response.data


def test_validate_application_api_reports_missing_fields():
    response = app.test_client().post(
        "/api/application/validate",
        json={"applicant_name": "Demo User", "location": "", "activity": "Coffee", "contact": ""},
    )

    assert response.status_code == 200
    result = response.get_json()["result"]
    assert result["valid"] is False
    assert "location" in result["missing_fields"]
    assert "contact" in result["missing_fields"]


def test_draft_api_creates_local_unsubmitted_draft():
    response = app.test_client().post(
        "/api/application/draft",
        json={
            "applicant_name": "Demo User",
            "location": "Demo Location",
            "activity": "Coffee cart",
            "contact": "demo@example.com",
        },
    )

    assert response.status_code == 200
    result = response.get_json()["result"]
    assert result["status"] == "awaiting_approval"
    assert result["submitted"] is False
    assert result["draft"]["applicant_name"] == "Demo User"


def test_draft_api_rejects_incomplete_application():
    response = app.test_client().post(
        "/api/application/draft",
        json={
            "applicant_name": "Demo User",
            "location": "",
            "activity": "Coffee cart",
            "contact": "",
        },
    )

    assert response.status_code == 422
    assert response.get_json()["result"]["status"] == "incomplete"


def test_application_api_rejects_unexpected_fields():
    response = app.test_client().post(
        "/api/application/validate",
        json={
            "applicant_name": "Demo User",
            "location": "Demo Location",
            "activity": "Coffee cart",
            "contact": "demo@example.com",
            "is_admin": True,
        },
    )

    assert response.status_code == 400
    assert "غير مسموحة" in response.get_json()["error"]


def test_application_api_rejects_non_text_values():
    response = app.test_client().post(
        "/api/application/validate",
        json={
            "applicant_name": 123,
            "location": "Demo Location",
            "activity": "Coffee cart",
            "contact": "demo@example.com",
        },
    )

    assert response.status_code == 400
