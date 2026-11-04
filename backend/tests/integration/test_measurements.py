import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.sensors.models import Sensor
from app.series.models import Series

URL = "/api/measurements"


@pytest.fixture
def sensor(db_session: Session, series: Series) -> Sensor:
    sensor = Sensor(name="T-01", series_id=series.id)
    db_session.add(sensor)
    db_session.commit()
    return sensor


def _post(client: TestClient, sensor_id: int, value: float, timestamp: str):
    return client.post(
        URL,
        params={"sensorId": sensor_id},
        json={"value": value, "timestamp": timestamp},
    )


def test_create_and_get_measurement(client: TestClient, sensor: Sensor):
    response = _post(client, sensor.id, 21.5, "2026-11-04T14:27:20.363Z")
    assert response.status_code == 201
    measurement = response.json()
    assert measurement == {
        "id": measurement["id"],
        "seriesId": sensor.series_id,
        "sensorId": sensor.id,
        "value": 21.5,
        "timestamp": "2026-11-04T14:27:20.363000Z",
    }

    response = client.get(f"{URL}/{measurement['id']}")
    assert response.json() == measurement


def test_value_outside_series_range_rejected(client: TestClient, sensor: Sensor):
    response = _post(client, sensor.id, 100, "2026-11-04T14:27:20Z")
    assert response.status_code == 422


def test_unknown_sensor_and_measurement_return_404(client: TestClient):
    assert _post(client, 999, 1, "2026-11-04T14:27:20Z").status_code == 404
    assert client.get(f"{URL}/999").status_code == 404


def test_list_filters_and_sort(client: TestClient, db_session: Session, sensor: Sensor):
    other_series = Series(
        name="Power", min_value=0, max_value=100, color="#000000", icon="x", unit="W"
    )
    db_session.add(other_series)
    db_session.commit()
    other_sensor = Sensor(name="P-01", series_id=other_series.id)
    db_session.add(other_sensor)
    db_session.commit()

    for day in (1, 2, 3):
        _post(client, sensor.id, day, f"2026-11-0{day}T00:00:00Z")
    _post(client, other_sensor.id, 50, "2026-11-02T00:00:00Z")

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
    assert client.get(URL, params={"series": "1,a"}).status_code == 422
    assert client.get(URL, params={"sort": "value"}).status_code == 422
