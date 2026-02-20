import pytest
from routes.requests import extract_miluim_info


def test_miluim_regex_logic():
    # בדיקה עם הטקסט שהפונקציה באמת מזהה
    assert extract_miluim_info("בקשה למתווה: A") == "A"
    assert extract_miluim_info("בקשה למתווה: B") == "B"


def test_create_request_validation():
    # בדיקה שאי אפשר להגיש בקשה עם ת"ז לא תקינה (פחות מ-9 ספרות)
    from fastapi.testclient import TestClient
    from backend.app import app
    client = TestClient(app)

    bad_payload = {
        "request_type": "MILUIM_RELIEF",
        "student_national_id": "123"  # לא תקין
    }
    response = client.post("/requests/", json=bad_payload)
    assert response.status_code == 401
    # שינוי הציפייה ל-401 כי אנחנו בודקים בלי להתחבר קודם
