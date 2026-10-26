from fastapi.testclient import TestClient
from app import main


class FakeSpan:
    def __init__(self):
        self.attributes = {}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def set_attribute(self, name, value):
        self.attributes[name] = value


class FakeTracer:
    def __init__(self):
        self.span = FakeSpan()

    def start_as_current_span(self, _):
        return self.span


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


def test_chat_emits_observability_attributes(tmp_path, monkeypatch):
    tracer = FakeTracer()
    monkeypatch.setattr(main.trace, "get_tracer", lambda _: tracer)
    main.settings.database_path = str(tmp_path / "api.db")
    with TestClient(main.app) as client:
        response = client.post("/v1/chat", json={"message": "¿Cómo solicito acceso VPN?", "thread_id": "trace-test"})
    assert response.status_code == 200
    assert tracer.span.attributes["session.id"] == "trace-test"
    assert tracer.span.attributes["rag.source_count"] >= 1
    assert tracer.span.attributes["output.value"] == response.json()["answer"]
