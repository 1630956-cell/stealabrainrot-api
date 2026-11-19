from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_brainrots():
    r = client.get("/brainrots")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 20


def test_search_and_filter():
    r = client.get("/brainrots", params={"rarity": "Secret"})
    assert r.status_code == 200
    assert all(b["rarity"] == "Secret" for b in r.json())
    assert len(r.json()) >= 3


def test_get_by_slug():
    r = client.get("/brainrots/trippi-troppi")
    assert r.status_code == 200
    assert r.json()["name"] == "Trippi Troppi"


def test_get_missing_404():
    assert client.get("/brainrots/does-not-exist").status_code == 404


def test_mutations_sorted():
    r = client.get("/mutations")
    assert r.status_code == 200
    multipliers = [m["multiplier"] for m in r.json()]
    assert multipliers == sorted(multipliers)
    assert len(multipliers) >= 15


def test_rainbow_multiplier():
    r = client.get("/mutations?permanent=true")
    rainbow = [m for m in r.json() if m["name"] == "Rainbow"]
    assert rainbow and rainbow[0]["multiplier"] == 10.0


def test_calculator():
    r = client.get("/calculator", params={"brainrot": "sammyni-spyderini", "mutation": "Rainbow", "traits": "Fire"})
    data = r.json()
    assert data["total_multiplier"] == 16.0
    assert data["income_per_second"] == 300000 * 16.0


def test_updates_latest():
    r = client.get("/updates/latest")
    assert r.status_code == 200


def test_admin_requires_key():
    assert client.post("/updates", json={"version": "x", "title": "x"}).status_code == 401


def test_admin_post_update():
    import uuid

    version = f"test-{uuid.uuid4().hex[:8]}"
    r = client.post(
        "/updates",
        json={"version": version, "title": "Test update", "source": "pytest", "new_brainrots": "Foo Bar"},
        headers={"X-API-Key": "change-me-dev-key"},
    )
    assert r.status_code == 201
    r = client.post(
        "/updates",
        json={"version": version, "title": "dup"},
        headers={"X-API-Key": "change-me-dev-key"},
    )
    assert r.status_code == 409


def test_admin_post_event_and_active_now():
    r = client.post(
        "/events",
        json={
            "name": "Test Molten",
            "event_type": "Molten",
            "starts_at": "2026-01-01T00:00:00Z",
            "ends_at": "2099-01-01T00:00:00Z",
        },
        headers={"X-API-Key": "change-me-dev-key"},
    )
    assert r.status_code == 201
    assert "Test Molten" in [e["name"] for e in client.get("/events/active-now").json()]
