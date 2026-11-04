# LogiAI

Application pédagogique de prédiction du risque de retard de livraison : modèle de régression logistique, API FastAPI sécurisée et formulaire web en français. Le modèle utilise des données synthétiques ; il doit être évalué sur des données réelles avant tout usage opérationnel.

## Installation

Prérequis : Python 3.11 ou 3.12 et Git.

```sh
git clone https://github.com/mccrking/LogiAI.git
cd LogiAI
python -m venv .venv
```

Activer l'environnement sous PowerShell :

```powershell
.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
```

Sous macOS / Linux :

```sh
source .venv/bin/activate
cp .env.example .env
```

Renseigner deux clés différentes dans `.env` (`LOGIAI_API_KEY` et `LOGIAI_ADMIN_KEY`), puis :

```sh
python -m pip install -r requirements.txt
python -m logiai.dataset
python -m logiai.train
python -m uvicorn logiai.api.main:app --reload
```

Ouvrir **http://localhost:8000** et saisir la clé utilisateur. La documentation interactive se trouve sur **http://localhost:8000/docs**. Les données et le modèle sont reproductibles (graine 42), générés localement et exclus de Git. Après un nouvel entraînement, redémarrer l'API pour recharger le modèle.

## API

| Route | Accès | Résultat |
|---|---|---|
| `GET /` | Public | Interface web |
| `GET /health` | Public | Statut et présence du modèle |
| `POST /v1/predict` | Clé utilisateur ou admin | Probabilité, alerte, seuil, version |
| `GET /v1/model-info` | Clé admin | Version et seuil du modèle |

Les clés sont transmises dans l'en-tête `X-API-Key`. Une clé absente ou invalide retourne **401**, un accès administrateur refusé **403**, des données invalides **422**, et un modèle absent **503**. Sans modèle, le serveur démarre et `/health` indique `model_loaded: false`.

Exemple de corps pour `/v1/predict` :

```json
{
  "distance_km": 120,
  "poids_kg": 450,
  "heure_depart": 17,
  "pluie_mm": 8,
  "trafic_index": 7.5,
  "nb_arrets": 4,
  "type_vehicule": "camion"
}
```

Les bornes sont décrites dans `/docs` et dans [le compte rendu](COMPTE_RENDU.md). Les champs supplémentaires sont refusés. Le seuil d'alerte est de 0,4.

## Client séparé et CORS

L'interface est directement servie par l'API. Pour l'exercice CORS, on peut aussi lancer dans un deuxième terminal :

```sh
python -m http.server 5500 --directory web
```

Ouvrir **http://localhost:5500**. Cette origine est explicitement autorisée ; le port 5501 ne l'est pas. CORS contrôle les navigateurs et ne remplace pas la clé API. Voir [la décision de sécurité](docs/adr/003-securite.md). Utiliser HTTPS lors d'une exposition distante de l'API.

## Vérification

```sh
python -m pytest -q
```

Les tests génèrent et entraînent leur propre modèle dans un dossier temporaire : aucun CSV, modèle préexistant ou fichier `.env` n'est requis. Ils couvrent les prédictions, les bornes, l'authentification, les rôles, CORS, l'interface et le démarrage sans modèle. GitHub Actions exécute la suite sous Python 3.11 et 3.12.

## Structure

- `logiai/dataset.py` : génération des données synthétiques.
- `logiai/train.py` : entraînement, évaluation et sauvegarde du pipeline.
- `logiai/predict.py` : chargement et inférence.
- `logiai/api/` : routes, schémas et sécurité.
- `web/index.html` : formulaire responsive, saisie des sept variables et gestion des erreurs.
- `tests/` : tests automatisés.
- `docs/adr/` : décisions d'architecture.
