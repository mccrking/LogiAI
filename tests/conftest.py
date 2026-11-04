import pytest
from fastapi.testclient import TestClient

from logiai.api.main import app


@pytest.fixture(scope="session", autouse=True)
def trained_model(tmp_path_factory):
    """Entraîne un modèle isolé, même après un clonage sans artefacts générés."""
    from logiai import train as training
    from logiai.api import main
    from logiai.dataset import make_dataset
    from logiai.predict import Predictor

    with pytest.MonkeyPatch.context() as patch:
        directory = tmp_path_factory.mktemp("model")
        data_path = directory / "livraisons.csv"
        model_path = directory / "model.joblib"
        info_path = directory / "model_info.json"
        make_dataset().to_csv(data_path, index=False)
        patch.setattr(training, "DATA_PATH", data_path)
        patch.setattr(training, "MODEL_PATH", model_path)
        patch.setattr(training, "INFO_PATH", info_path)
        training.train()
        patch.setattr(main, "MODEL_PATH", model_path)
        patch.setattr(main, "Predictor", lambda path: Predictor(path, info_path))
        yield

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
