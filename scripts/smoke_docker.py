"""Vérifie la pile réelle : python scripts/smoke_docker.py [--url URL]."""
import argparse
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from dotenv import dotenv_values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://localhost:8080")
    args = parser.parse_args()
    base = args.url.rstrip("/")
    root = Path(__file__).resolve().parents[1]
    key = os.getenv("LOGIAI_API_KEY") or dotenv_values(root / ".env").get("LOGIAI_API_KEY")
    if not key:
        parser.error("Configurer LOGIAI_API_KEY dans l'environnement ou dans .env.")
    delivery = json.loads((root / "livraison.json").read_text(encoding="utf-8"))

    def call(path, expected, body=None, api_key=None):
        headers = {"Content-Type": "application/json"}
        if api_key is not None:
            headers["X-API-Key"] = api_key
        request = Request(base + path, data=json.dumps(body).encode() if body is not None else None, headers=headers)
        try:
            response = urlopen(request, timeout=15)
        except HTTPError as error:
            response = error
        with response:
            status, content = response.code, response.read()
        assert status == expected, f"{path} : attendu {expected}, obtenu {status}"
        print(f"{path} : HTTP {status}")
        return content

    page = call("/", 200).decode()
    assert "const API_URL = '/api/v1/predict'" in page
    health = json.loads(call("/api/health", 200))
    assert health == {"status": "ok", "model_loaded": True}
    call("/api/v1/predict", 401, delivery)
    call("/api/v1/predict", 401, delivery, "cle-volontairement-incorrecte")
    prediction = json.loads(call("/api/v1/predict", 200, delivery, key))
    assert 0 <= prediction["probabilite_retard"] <= 1
    assert prediction["alerte"] == (prediction["probabilite_retard"] >= prediction["seuil"])
    call("/api/v1/predict", 422, {**delivery, "distance_km": -1}, key)
    call("/api/v1/model-info", 403, api_key=key)
    assert "./openapi.json" in call("/api/docs", 200).decode()
    schema = json.loads(call("/api/openapi.json", 200))
    assert "/v1/predict" in schema["paths"]
    print("Prédiction : " + json.dumps(prediction, ensure_ascii=False))
    print("Vérification de la pile Docker réussie.")


if __name__ == "__main__":
    main()
