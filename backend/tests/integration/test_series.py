from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.measurements.models import Measurement
from app.sensors.models import Sensor
from app.series.models import Series

URL = "/api/series"
PAYLOAD = {
    "name": "Humidity",
    "minValue": 0,
    "maxValue": 100,
    "color": "#1f77b4",
    "icon": "water_drop",
    "unit": "%",
}


def test_series_crud(client: TestClient):
    response = client.post(URL, json=PAYLOAD)
    assert response.status_code == 201
    series = response.json()
    assert series == {**PAYLOAD, "id": series["id"]}

    assert client.get(URL).json() == [series]
    assert client.get(f"{URL}/{series['id']}").json() == series

    updated = {**PAYLOAD, "name": "Relative humidity", "maxValue": 110}
    response = client.put(f"{URL}/{series['id']}", json=updated)
    assert response.status_code == 200
    assert response.json() == {**updated, "id": series["id"]}

    assert client.delete(f"{URL}/{series['id']}").status_code == 204
    assert client.get(f"{URL}/{series['id']}").status_code == 404


def test_invalid_series_rejected(client: TestClient, series: Series):
    assert client.post(URL, json={**PAYLOAD, "minValue": 200}).status_code == 422
    assert client.post(URL, json={**PAYLOAD, "color": "blue"}).status_code == 422
    assert client.post(URL, json={**PAYLOAD, "name": series.name}).status_code == 409

    other = client.post(URL, json=PAYLOAD).json()
    response = client.put(f"{URL}/{other['id']}", json={**PAYLOAD, "name": series.name})
    assert response.status_code == 409


def test_missing_series_returns_404(client: TestClient):
    assert client.get(f"{URL}/999").status_code == 404
    assert client.put(f"{URL}/999", json=PAYLOAD).status_code == 404
    assert client.delete(f"{URL}/999").status_code == 404


def test_delete_series_removes_sensors_and_measurements(
    client: TestClient, db_session: Session, series: Series
):
    sensor = Sensor(name="T-01", series_id=series.id)
    db_session.add(sensor)
    db_session.commit()
    response = client.post(
        "/api/measurements",
        params={"sensorId": sensor.id},
        json={"value": 20, "timestamp": "2026-11-04T12:00:00Z"},
    )
    assert response.status_code == 201

    assert client.delete(f"{URL}/{series.id}").status_code == 204
    db_session.expire_all()
    assert db_session.scalar(select(func.count()).select_from(Sensor)) == 0
    assert db_session.scalar(select(func.count()).select_from(Measurement)) == 0


def test_delete_sensor_keeps_measurements(
    client: TestClient, db_session: Session, series: Series
):
    sensor = Sensor(name="T-01", series_id=series.id)
    db_session.add(sensor)
    db_session.commit()
    measurement = client.post(
        "/api/measurements",
        params={"sensorId": sensor.id},
        json={"value": 20, "timestamp": "2026-11-04T12:00:00Z"},
    ).json()

    assert client.delete(f"/api/v1/sensors/{sensor.id}").status_code == 204
    response = client.get(f"/api/measurements/{measurement['id']}")
    assert response.json() == {**measurement, "sensorId": None}
