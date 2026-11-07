from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.measurements.models import Measurement
from app.sensors.models import Sensor
from app.series.models import Series
from tests.helpers import create_sensor, post_measurement

URL = "/api/series"
PAYLOAD = {
    "name": "Humidity",
    "minValue": 0,
    "maxValue": 100,
    "color": "#1f77b4",
    "icon": "water_drop",
    "unit": "%",
}


def test_series_crud(admin_client: TestClient):
    response = admin_client.post(URL, json=PAYLOAD)
    assert response.status_code == 201
    series = response.json()
    assert series == {**PAYLOAD, "id": series["id"]}
    assert response.headers["Location"] == f"{URL}/{series['id']}"

    assert admin_client.get(URL).json() == [series]
    assert admin_client.get(f"{URL}/{series['id']}").json() == series

    updated = {**PAYLOAD, "name": "Relative humidity", "maxValue": 110}
    response = admin_client.put(f"{URL}/{series['id']}", json=updated)
    assert response.status_code == 200
    assert response.json() == {**updated, "id": series["id"]}

    assert admin_client.delete(f"{URL}/{series['id']}").status_code == 204
    assert admin_client.get(f"{URL}/{series['id']}").status_code == 404


def test_icon_and_unit_are_optional(admin_client: TestClient):
    payload = {"name": "Count", "minValue": 0, "maxValue": 10, "color": "#000000"}
    response = admin_client.post(URL, json=payload)
    assert response.status_code == 201
    assert response.json() == {
        **payload,
        "icon": None,
        "unit": None,
        "id": response.json()["id"],
    }


def test_invalid_series_rejected(admin_client: TestClient, series: Series):
    assert admin_client.post(URL, json={**PAYLOAD, "minValue": 200}).status_code == 422
    # The range must not be empty: minValue < maxValue.
    assert admin_client.post(URL, json={**PAYLOAD, "minValue": 100}).status_code == 422
    assert admin_client.post(URL, json={**PAYLOAD, "unit": "x" * 21}).status_code == 422
    assert (
        admin_client.post(URL, json={**PAYLOAD, "name": "x" * 101}).status_code == 422
    )
    assert admin_client.post(URL, json={**PAYLOAD, "color": "blue"}).status_code == 422
    assert (
        admin_client.post(URL, json={**PAYLOAD, "name": series.name}).status_code == 409
    )

    other = admin_client.post(URL, json=PAYLOAD).json()
    response = admin_client.put(
        f"{URL}/{other['id']}", json={**PAYLOAD, "name": series.name}
    )
    assert response.status_code == 409


def test_missing_series_returns_404(admin_client: TestClient):
    assert admin_client.get(f"{URL}/999").status_code == 404
    assert admin_client.put(f"{URL}/999", json=PAYLOAD).status_code == 404
    assert admin_client.delete(f"{URL}/999").status_code == 404


def test_delete_series_removes_sensors_and_measurements(
    admin_client: TestClient, db_session: Session, series: Series
):
    _, api_key = create_sensor(db_session, series.id)
    response = post_measurement(admin_client, api_key, 20, "2026-11-04T12:00:00Z")
    assert response.status_code == 201

    assert admin_client.delete(f"{URL}/{series.id}").status_code == 204
    db_session.expire_all()
    assert db_session.scalar(select(func.count()).select_from(Sensor)) == 0
    assert db_session.scalar(select(func.count()).select_from(Measurement)) == 0


def test_delete_sensor_keeps_measurements(
    admin_client: TestClient, db_session: Session, series: Series
):
    sensor, api_key = create_sensor(db_session, series.id)
    measurement = post_measurement(
        admin_client, api_key, 20, "2026-11-04T12:00:00Z"
    ).json()

    assert admin_client.delete(f"/api/sensors/{sensor.id}").status_code == 204
    response = admin_client.get(f"/api/measurements/{measurement['id']}")
    # sensorId is left out once the sensor is gone.
    del measurement["sensorId"]
    assert response.json() == measurement


def test_update_range_excluding_measurements_returns_409(
    admin_client: TestClient, db_session: Session, series: Series
):
    _, api_key = create_sensor(db_session, series.id)
    response = post_measurement(admin_client, api_key, 10, "2026-01-10T10:00:00Z")
    assert response.status_code == 201
    payload = {**PAYLOAD, "name": series.name}

    narrowed = {**payload, "minValue": 50, "maxValue": 60}
    assert admin_client.put(f"{URL}/{series.id}", json=narrowed).status_code == 409
    db_session.refresh(series)
    assert series.min_value != 50

    # Bounds are inclusive: a range ending exactly on the stored value is fine.
    edge = {**payload, "minValue": 10, "maxValue": 60}
    assert admin_client.put(f"{URL}/{series.id}", json=edge).status_code == 200
