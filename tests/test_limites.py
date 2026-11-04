import pytest

from tests.conftest import VALID

CAS_LIMITES = [
    ("distance min dedans", "distance_km", 1, 200),
    ("distance min dehors", "distance_km", 0.9, 422),
    ("distance max dedans", "distance_km", 1000, 200),
    ("distance max dehors", "distance_km", 1000.1, 422),
    ("poids min dedans", "poids_kg", 0.1, 200),
    ("poids min dehors", "poids_kg", 0, 422),
    ("poids max dedans", "poids_kg", 5000, 200),
    ("poids max dehors", "poids_kg", 5000.1, 422),
    ("heure min dedans", "heure_depart", 0, 200),
    ("heure min dehors", "heure_depart", -1, 422),
    ("heure max dedans", "heure_depart", 23, 200),
    ("heure max dehors", "heure_depart", 24, 422),
    ("pluie min dedans", "pluie_mm", 0, 200),
    ("pluie min dehors", "pluie_mm", -0.1, 422),
    ("pluie max dedans", "pluie_mm", 100, 200),
    ("pluie max dehors", "pluie_mm", 100.1, 422),
    ("trafic min dedans", "trafic_index", 0, 200),
    ("trafic min dehors", "trafic_index", -0.1, 422),
    ("trafic max dedans", "trafic_index", 10, 200),
    ("trafic max dehors", "trafic_index", 10.1, 422),
    ("arrêts min dedans", "nb_arrets", 0, 200),
    ("arrêts min dehors", "nb_arrets", -1, 422),
    ("arrêts max dedans", "nb_arrets", 50, 200),
    ("arrêts max dehors", "nb_arrets", 51, 422),
    ("heure décimale", "heure_depart", 11.5, 422),
]


@pytest.mark.parametrize("description, champ, valeur, attendu", CAS_LIMITES)
def test_bornes(description, champ, valeur, attendu, client, headers_user):
    response = client.post(
        "/v1/predict", json={**VALID, champ: valeur}, headers=headers_user
    )
    assert response.status_code == attendu, description
