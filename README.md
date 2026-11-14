# LogiAI — Atelier 5

Conteneurisation de l’API de prédiction des retards de livraison avec Docker,
Nginx et Docker Compose. Projet réalisé par **Mehdi Chmiti et Ismail Haddaoui**,
sous l’encadrement de **Mme Soukaina Gouraguine**.

Le modèle utilise des données synthétiques : ses probabilités doivent être
validées sur des données réelles avant un usage opérationnel.

## Démarrage sous Windows avec Docker uniquement

Prérequis : Git et Docker Desktop démarré avec le moteur Linux. Python n’est pas
nécessaire sur Windows pour cette procédure.

```powershell
git clone --branch atelier5 https://github.com/mccrking/LogiAI.git
cd LogiAI
docker info
Copy-Item .env.example .env
```

Remplacer les deux valeurs de `.env` par des clés différentes, longues et
aléatoires : `LOGIAI_API_KEY` et `LOGIAI_ADMIN_KEY`. Ne jamais publier ce fichier.
Sur le dossier déjà configuré, conserver le `.env` existant.

Les données et le modèle sont exclus de Git. Après un nouveau clonage, les
préparer explicitement avec le conteneur d’entraînement :

```powershell
.\scripts\prepare-model.ps1
```

Ce script construit l’étape `trainer` et écrit `data/livraisons.csv`,
`models/model.joblib` et `models/model_info.json` dans les dossiers locaux.
Puis démarrer l’ensemble :

```powershell
docker compose config --quiet
docker compose up -d --build --wait --wait-timeout 120
docker compose ps
```

- Page : **http://localhost:8080** — saisir la valeur de `LOGIAI_API_KEY`.
- API directe : **http://localhost:8001/health**.
- Swagger : **http://localhost:8001/docs**, ou **http://localhost:8080/api/docs**.

Les ports sont liés à `127.0.0.1` : ils sont accessibles depuis cette machine.
Compose attend que l’API réponde avec un modèle chargé avant de lancer Nginx.
Les clés sont injectées à l’exécution avec `env_file`, jamais intégrées à l’image.

### Accès depuis le réseau local

Pour présenter la page à une autre machine du même réseau, ajouter
`LOGIAI_WEB_BIND=0.0.0.0` dans le `.env` local puis exécuter
`docker compose up -d --wait`. Utiliser alors `http://IP-DU-PC:8080`.
Le pare-feu doit autoriser le TCP 8080 depuis le sous-réseau local. L’API directe
sur 8001 reste limitée au PC ; le navigateur distant passe par Nginx et utilise
la clé utilisateur. Cette option ne publie pas le site sur Internet.

## Préparation sous Linux ou macOS

Créer `.env` à partir de `.env.example` et y configurer les clés, puis :

```sh
mkdir -p data models
docker build --target trainer -t logiai-trainer:1.0 .
docker run --rm --user "$(id -u):$(id -g)" \
  --mount "type=bind,source=$(pwd)/data,target=/app/data" \
  --mount "type=bind,source=$(pwd)/models,target=/app/models" \
  logiai-trainer:1.0
docker compose up -d --build --wait --wait-timeout 120
```

## Architecture

```text
Navigateur http://localhost:8080
  POST /api/v1/predict avec X-API-Key
    -> Nginx web:80
       -> FastAPI api:8000/v1/predict
          -> modèle chargé depuis /app/models
```

Le slash final de `proxy_pass http://api:8000/` retire le préfixe `/api/`.
Le navigateur reste sur la même origine : il ne résout jamais le nom Docker
`api` et n’a pas de prérequête CORS à effectuer. La clé reste vérifiée par FastAPI.

Les fichiers du modèle et les données sont copiés dans l’image autonome et
montés en lecture seule dans Compose. Après réentraînement, redémarrer l’API
pour recharger le modèle ; après modification de code, reconstruire l’image.
Voir [ADR 004](docs/adr/004-docker.md).

## Vérification

Avec Python 3.12 et un environnement virtuel :

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe scripts/smoke_docker.py
```

`requirements-runtime.txt` fixe les versions des dépendances principales de
l’API et du modèle. `requirements.txt` ajoute les outils de test. La suite pytest
entraîne ses propres artefacts temporaires et contient **55 tests**. Le script
smoke vérifie la pile réelle via Nginx, notamment les codes **200, 401, 422 et 403**,
le schéma OpenAPI et le chargement du modèle. Il ne journalise jamais la clé.

Les workflows GitHub Actions vérifient les tests Python et la construction de
la pile Docker avec un appel de prédiction. Leur état est visible dans l’onglet
Actions du dépôt.

## API

| Route directe | Accès | Fonction |
|---|---|---|
| `GET /` | Public | Redirection vers la documentation |
| `GET /health` | Public | Statut et présence du modèle |
| `GET /docs` | Public | Documentation interactive |
| `POST /v1/predict` | Utilisateur ou admin | Risque, alerte, seuil et version |
| `GET /v1/model-info` | Admin | Version et seuil du modèle |

Par Nginx, ajouter `/api` devant la route. Exemple de corps :
[livraison.json](livraison.json). Une clé absente ou invalide retourne **401**,
un rôle insuffisant **403**, une entrée invalide **422**, et un modèle absent
**503**. Nginx retourne **502** ou **504** lorsque l’API est arrêtée ; la page explique cette
indisponibilité. Le seuil d’alerte est de **40 %**.

## Commandes utiles

```powershell
docker compose logs --tail=30 api
docker compose logs -f api
docker stats --no-stream logiai-api
docker compose exec api ls /app/models
docker compose stop api
docker compose start --wait api
docker compose stop
docker compose start --wait
docker compose down
```

`Ctrl+C` quitte le suivi des logs. `down` supprime les conteneurs et le réseau,
mais conserve les dossiers locaux `data/` et `models/`. Après une modification :

```powershell
docker compose up -d --build --wait --wait-timeout 120
```

Si l’API a été recréée avec une autre adresse IP interne, redémarrer aussi le
service web pour que Nginx résolve à nouveau le nom `api`.

## Livrables

- [Compte rendu de l’atelier 5](COMPTE_RENDU.md).
- [Compte rendu de l’atelier 5 au format PDF](docs/Compte_rendu_Atelier_5_LogiAI.pdf).
- [Décisions Docker](docs/adr/004-docker.md).
- [Propositions de tickets de sortie](docs/TICKETS_SORTIE.md).
- [Compte rendu conservé de l’atelier 4](docs/COMPTE_RENDU_ATELIER4.md).

Le rendu passe par une pull request avec relecture réelle du binôme, puis fusion
avec un commit de merge et création du tag `tp5`. Les clés et les artefacts
entraînés restent exclus de Git.
