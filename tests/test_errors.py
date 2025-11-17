import json

from fastapi.testclient import TestClient

from app.core.error_handler import problem
from app.main import app


def test_rfc7807_contract():
    resp = problem(
        400, "Bad Request", "invalid ingredients", type_="invalid-ingredients"
    )
    try:
        resp.render()
    except Exception:
        pass
    body = json.loads(resp.body)

    assert set(["type", "title", "status", "detail", "correlation_id"]).issubset(
        set(body.keys())
    )
    assert body["status"] == 400
    assert body["type"] == "invalid-ingredients"
    assert isinstance(body["correlation_id"], str) and len(body["correlation_id"]) >= 20


client = TestClient(app)


def test_not_found_item():
    r = client.get("/items/999")
    assert r.status_code == 404
    body = r.json()
    assert "error" in body and body["error"]["code"] == "not_found"


def test_validation_error():
    r = client.post("/items", params={"name": ""})
    assert r.status_code == 422
    body = r.json()
    assert body["error"]["code"] == "validation_error"
