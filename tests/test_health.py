import app.main as main_module


def test_basic_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_full_health_when_everything_is_up(client):
    response = client.get("/health/full")

    assert response.status_code == 200
    assert response.json()["database"] == "connected"
    assert response.json()["redis"] == "connected"


def test_redis_down_returns_503(client, broken_redis):
    redis_response = client.get("/health/redis")
    full_response = client.get("/health/full")

    assert redis_response.status_code == 503
    assert full_response.status_code == 503
    assert full_response.json()["redis"] == "disconnected"
    assert full_response.json()["database"] == "connected"


def test_database_down_returns_503(client, monkeypatch):
    class BrokenSession:
        def execute(self, *args, **kwargs):
            raise ConnectionError("Database is down")

        def close(self):
            pass

    monkeypatch.setattr(main_module, "SessionLocal", BrokenSession)

    db_response = client.get("/health/db")
    full_response = client.get("/health/full")

    assert db_response.status_code == 503
    assert full_response.status_code == 503
    assert full_response.json()["database"] == "disconnected"


def test_root_and_info(client):
    assert client.get("/").status_code == 200
    assert client.get("/info").json()["name"] == "FinFlow API"
