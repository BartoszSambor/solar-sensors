from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth.security import generate_token, hash_token
from app.sensors.models import Sensor


def create_sensor(
    db: Session, series_id: int, name: str = "T-01"
) -> tuple[Sensor, str]:
    """Creates a sensor directly in the DB; returns it with its API key."""
    api_key = generate_token()
    sensor = Sensor(name=name, series_id=series_id, api_key_hash=hash_token(api_key))
    db.add(sensor)
    db.commit()
    return sensor, api_key


def post_measurement(client: TestClient, api_key: str, value: float, timestamp: str):
    return client.post(
        "/api/measurements",
        headers={"X-API-Key": api_key},
        json={"value": value, "timestamp": timestamp},
    )
