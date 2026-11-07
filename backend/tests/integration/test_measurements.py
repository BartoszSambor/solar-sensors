from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.sensors.models import Sensor
from app.series.models import Series
from tests.helpers import create_sensor, post_measurement

URL = "/api/measurements"


@pytest.fixture
def sensor_with_key(db_session: Session, series: Series) -> tuple[Sensor, str]:
    return create_sensor(db_session, series.id)


def test_create_and_get_measurement(
    client: TestClient, sensor_with_key: tuple[Sensor, str]
):
    sensor, api_key = sensor_with_key
    response = post_measurement(client, api_key, 21.5, "2026-11-04T14:27:20.363Z")
    assert response.status_code == 201
    measurement = response.json()
    assert response.headers["Location"] == f"{URL}/{measurement['id']}"
    assert measurement == {
        "id": measurement["id"],
        "seriesId": sensor.series_id,
        "sensorId": sensor.id,
        "value": 21.5,
        "timestamp": "2026-11-04T14:27:20.363000Z",
    }

    response = client.get(f"{URL}/{measurement['id']}")
    assert response.json() == measurement


def test_timestamp_defaults_to_now(
    client: TestClient, sensor_with_key: tuple[Sensor, str]
):
    _, api_key = sensor_with_key
    before = datetime.now(UTC)
    response = client.post(URL, headers={"X-API-Key": api_key}, json={"value": 1})
    assert response.status_code == 201
    timestamp = datetime.fromisoformat(response.json()["timestamp"])
    assert before <= timestamp <= datetime.now(UTC)


def test_sensor_last_measurement_at(
    admin_client: TestClient, sensor_with_key: tuple[Sensor, str]
):
    sensor, api_key = sensor_with_key
    sensor_url = f"/api/sensors/{sensor.id}"

    def last() -> str | None:
        return admin_client.get(sensor_url).json()["lastMeasurementAt"]

    assert last() is None
    post_measurement(admin_client, api_key, 1, "2026-11-04T12:00:00Z")
    assert last() == "2026-11-04T12:00:00Z"
    # A late, older measurement doesn't move it back.
    post_measurement(admin_client, api_key, 2, "2026-11-04T11:00:00Z")
    assert last() == "2026-11-04T12:00:00Z"
    post_measurement(admin_client, api_key, 3, "2026-11-04T13:00:00Z")
    assert last() == "2026-11-04T13:00:00Z"


def test_sensor_id_param_is_ignored(
    client: TestClient, db_session: Session, sensor_with_key: tuple[Sensor, str]
):
    sensor, api_key = sensor_with_key
    other, _ = create_sensor(db_session, sensor.series_id, name="T-02")
    response = client.post(
        URL,
        params={"sensorId": other.id},
        headers={"X-API-Key": api_key},
        json={"value": 1, "timestamp": "2026-11-04T14:27:20Z"},
    )
    assert response.json()["sensorId"] == sensor.id


def test_value_outside_series_range_rejected(
    client: TestClient, sensor_with_key: tuple[Sensor, str]
):
    _, api_key = sensor_with_key
    response = post_measurement(client, api_key, 100, "2026-11-04T14:27:20Z")
    assert response.status_code == 422


def test_future_timestamp_rejected(
    client: TestClient, sensor_with_key: tuple[Sensor, str]
):
    _, api_key = sensor_with_key
    now = datetime.now(UTC)
    late = (now + timedelta(minutes=10)).isoformat()
    assert post_measurement(client, api_key, 1, late).status_code == 422
    # Small clock drift is tolerated.
    near = (now + timedelta(minutes=1)).isoformat()
    assert post_measurement(client, api_key, 1, near).status_code == 201


def test_missing_or_invalid_api_key_rejected(
    client: TestClient, admin_client: TestClient
):
    body = {"value": 1, "timestamp": "2026-11-04T14:27:20Z"}
    assert client.post(URL, json=body).status_code == 401
    assert post_measurement(client, "wrong", 1, body["timestamp"]).status_code == 401
    # A user's bearer token is not a sensor key.
    assert admin_client.post(URL, json=body).status_code == 401


def test_deleted_sensor_key_rejected(
    admin_client: TestClient, sensor_with_key: tuple[Sensor, str]
):
    sensor, api_key = sensor_with_key
    assert admin_client.delete(f"/api/sensors/{sensor.id}").status_code == 204
    response = post_measurement(admin_client, api_key, 1, "2026-11-04T14:27:20Z")
    assert response.status_code == 401


def test_missing_measurement_returns_404(client: TestClient):
    assert client.get(f"{URL}/999").status_code == 404


def test_list_filters_and_sort(
    client: TestClient, db_session: Session, sensor_with_key: tuple[Sensor, str]
):
    sensor, api_key = sensor_with_key
    other_series = Series(
        name="Power", min_value=0, max_value=100, color="#000000", icon="x", unit="W"
    )
    db_session.add(other_series)
    db_session.commit()
    _, other_key = create_sensor(db_session, other_series.id, name="P-01")

    for day in (1, 2, 3):
        post_measurement(client, api_key, day, f"2026-11-0{day}T00:00:00Z")
    post_measurement(client, other_key, 50, "2026-11-02T00:00:00Z")

    values = [m["value"] for m in client.get(URL).json()]
    assert values == [1, 2, 50, 3]

    params = {"series": str(sensor.series_id), "sort": "-timestamp"}
    values = [m["value"] for m in client.get(URL, params=params).json()]
    assert values == [3, 2, 1]

    params = {
        "series": f"{sensor.series_id},{other_series.id}",
        "from": "2026-11-02T00:00:00Z",
        "to": "2026-11-02T23:59:59Z",
    }
    values = [m["value"] for m in client.get(URL, params=params).json()]
    assert sorted(values) == [2, 50]

    values = [m["value"] for m in client.get(URL, params={"limit": 2}).json()]
    assert values == [1, 2]


def test_list_rejects_invalid_params(client: TestClient):
    assert client.get(URL, params={"series": "1,a"}).status_code == 400
    assert client.get(URL, params={"sort": "value"}).status_code == 400
    assert client.get(URL, params={"limit": 0}).status_code == 400
