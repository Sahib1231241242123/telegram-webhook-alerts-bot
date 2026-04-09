from fastapi.testclient import TestClient

import app.main as main_module


class DummyQueue:
    def __init__(self):
        self.items = []

    async def put(self, value):
        self.items.append(value)


def test_webhook_accepts_valid_update(monkeypatch) -> None:
    dummy_queue = DummyQueue()
    monkeypatch.setattr(main_module.telegram_app, "update_queue", dummy_queue)
    app = main_module.create_fastapi_app(enable_lifespan=False)
    client = TestClient(app)

    response = client.post("/webhook", json={"update_id": 1000})
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert len(dummy_queue.items) == 1


def test_webhook_rejects_invalid_payload() -> None:
    app = main_module.create_fastapi_app(enable_lifespan=False)
    client = TestClient(app)

    response = client.post("/webhook", json=["bad"])
    assert response.status_code == 400


def test_health_endpoint() -> None:
    app = main_module.create_fastapi_app(enable_lifespan=False)
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
