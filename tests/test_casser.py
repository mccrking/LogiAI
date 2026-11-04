import pytest

from tests.conftest import VALID

CAS_REFUSES = [
    ("champ manquant", "/v1/predict",
     {k: v for k, v in VALID.items() if k != "poids_kg"}, 422),
    ("valeur absurde", "/v1/predict", {**VALID, "poids_kg": 99999}, 422),
    ("texte au lieu d'un nombre", "/v1/predict", {**VALID, "pluie_mm": "forte"}, 422),
    ("champ en trop", "/v1/predict", {**VALID, "couleur": "rouge"}, 422),
    ("mauvaise route", "/v1/not-found", VALID, 404),
]


@pytest.mark.parametrize("description, url, corps, attendu", CAS_REFUSES)
def test_request_refuse(client, description, url, corps, attendu, headers_user):
    response = client.post(url, json=corps, headers=headers_user)
    assert response.status_code == attendu, description
