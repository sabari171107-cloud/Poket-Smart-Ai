from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_local_analysis():
    response = client.post(
        "/api/analyze",
        json={
            "monthly_income": 50000,
            "expenses": [{"category": "Rent", "amount": 15000}],
            "savings_goal": 10000,
            "provider": "local",
            "currency": "INR",
        },
    )
    assert response.status_code == 200
    assert response.json()["summary"]["remaining"] == 35000
