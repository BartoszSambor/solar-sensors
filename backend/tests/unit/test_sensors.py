from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth.security import hash_token
from app.sensors.models import Sensor
from app.series.models import Series


def test_sensor_crud(admin_client: TestClient, db_session: Session, series: Series):
    response = admin_client.post(
        "/api/sensors", json={"name": "PV-01", "seriesId": series.id}
    )
    assert response.status_code == 201
    created = response.json()
    assert response.headers["Location"] == f"/api/sensors/{created['id']}"
    api_key = created.pop("apiKey")
    sensor = created
    assert sensor["name"] == "PV-01"
    assert sensor["seriesId"] == series.id
    assert sensor["createdAt"]
    assert sensor["lastMeasurementAt"] is None

    # Only the hash is stored, and the key is never returned again.
    stored = db_session.get(Sensor, sensor["id"])
    assert stored is not None
    assert stored.api_key_hash == hash_token(api_key)

    response = admin_client.get("/api/sensors")
    assert response.json() == [sensor]

    response = admin_client.get(f"/api/sensors/{sensor['id']}")
    assert response.json() == sensor

    response = admin_client.delete(f"/api/sensors/{sensor['id']}")
    assert response.status_code == 204
    assert admin_client.get(f"/api/sensors/{sensor['id']}").status_code == 404


def test_sensor_with_unknown_series_rejected(admin_client: TestClient):
    response = admin_client.post(
        "/api/sensors", json={"name": "PV-01", "seriesId": 999}
    )
    assert response.status_code == 422


def test_missing_sensor_returns_404(admin_client: TestClient):
    assert admin_client.get("/api/sensors/999").status_code == 404
    assert admin_client.delete("/api/sensors/999").status_code == 404


def test_each_sensor_gets_its_own_key(admin_client: TestClient, series: Series):
    keys = {
        admin_client.post(
            "/api/sensors", json={"name": name, "seriesId": series.id}
        ).json()["apiKey"]
        for name in ("A", "B")
    }
    assert len(keys) == 2
