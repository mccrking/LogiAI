from tests.conftest import VALID


def test_predict_sans_cle_renvoie_401(client):
    assert client.post("/v1/predict", json=VALID).status_code == 401


def test_predict_fausse_cle_renvoie_401(client):
    assert client.post(
        "/v1/predict", json=VALID, headers={"X-API-Key": "wrong"}
    ).status_code == 401


def test_predict_cle_utilisateur_renvoie_200(client, headers_user):
    assert client.post(
        "/v1/predict", json=VALID, headers=headers_user
    ).status_code == 200


def test_model_info_cle_utilisateur_renvoie_403(client, headers_user):
    assert client.get("/v1/model-info", headers=headers_user).status_code == 403


def test_model_info_cle_admin_renvoie_200(client, headers_admin):
    assert client.get("/v1/model-info", headers=headers_admin).status_code == 200


def test_model_info_sans_cle_renvoie_401(client):
    assert client.get("/v1/model-info").status_code == 401


def test_health_reste_public(client):
    assert client.get("/health").status_code == 200


def test_origine_autorisee(client, headers_user):
    response = client.options(
        "/v1/predict",
        headers={
            **headers_user,
            "Origin": "http://localhost:5500",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,x-api-key",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5500"


def test_origine_inconnue_refusee(client):
    response = client.options(
        "/v1/predict",
        headers={
            "Origin": "http://localhost:5501",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" not in response.headers
