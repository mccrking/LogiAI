import pytest
from fastapi.testclient import TestClient

from logiai.api.main import app

VALID = {
    "distance_km": 120.0,
    "poids_kg": 450.0,
    "heure_depart": 17,
    "pluie_mm": 8.0,
    "trafic_index": 7.5,
    "nb_arrets": 4,
    "type_vehicule": "camion",
}


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def headers_user(monkeypatch):
    from logiai import config

    monkeypatch.setattr(config, "API_KEY", "test-user-key")
    return {"X-API-Key": "test-user-key"}


@pytest.fixture
def headers_admin(monkeypatch):
    from logiai import config

    monkeypatch.setattr(config, "ADMIN_KEY", "test-admin-key")
    return {"X-API-Key": "test-admin-key"}
