"""Prédiction hors API : logiai-predict livraison.json."""
import argparse
import json
import sys
from pathlib import Path

from logiai.config import ALERT_THRESHOLD, MODEL_PATH
from logiai.predict import Predictor


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="logiai-predict")
    parser.add_argument("fichier", help="fichier JSON d'une livraison")
    args = parser.parse_args(argv)
    chemin = Path(args.fichier)
    if not chemin.is_file():
        print(f"Fichier introuvable : {chemin}", file=sys.stderr)
        return 1
    try:
        livraison = json.loads(chemin.read_text(encoding="utf-8-sig"))
        if not isinstance(livraison, dict):
            raise ValueError("Le JSON doit contenir un objet livraison")
        if not MODEL_PATH.is_file():
            print(f"Modèle introuvable : {MODEL_PATH}. Définissez LOGIAI_HOME vers le dossier contenant models/.", file=sys.stderr)
            return 1
        predictor = Predictor()
        result = predictor.predict(livraison)
        proba = result["probabilite_retard"]
        seuil = result.get("seuil", ALERT_THRESHOLD)
        statut = "ALERTE" if result["alerte"] else "PAS D'ALERTE"
        print(f"Probabilité de retard : {round(proba * 100)} % ({statut}) - seuil : {seuil:g}")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Prédiction impossible : {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
