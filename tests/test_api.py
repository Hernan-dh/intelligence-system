from fastapi.testclient import TestClient
from app import main


def test_health_and_contract(tmp_path):
    main.settings.database_path = str(tmp_path / "api.db")
    with TestClient(main.app) as client:
        health = client.get("/health")
        response = client.post("/v1/chat", json={"message": "¿Cómo solicito acceso VPN?", "thread_id": "api-test"})
    assert health.status_code == 200
    assert response.status_code == 200
    body = response.json()
    assert body["sources"][0]["document_id"] == "vpn"
    assert body["thread_id"] == "api-test"
