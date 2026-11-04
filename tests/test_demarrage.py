from fastapi.testclient import TestClient

from logiai.api import main
from tests.conftest import VALID


def test_interface_web(client):
    response = client.get("/")
    assert response.status_code == 200
    assert 'id="livraison"' in response.text
    assert "text/html" in response.headers["content-type"]


def test_demarrage_sans_modele(tmp_path, monkeypatch, headers_user, headers_admin):
    monkeypatch.setattr(main, "MODEL_PATH", tmp_path / "absent.joblib")
    with TestClient(main.app) as client:
        assert client.get("/health").json() == {"status": "ok", "model_loaded": False}
        assert client.post("/v1/predict", json=VALID, headers=headers_user).status_code == 503
        assert client.get("/v1/model-info", headers=headers_admin).status_code == 503
    assert main.state == {}
