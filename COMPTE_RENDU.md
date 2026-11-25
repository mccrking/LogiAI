# Atelier 6 - Faire de LogiAI un package

**Étudiants :** Mehdi Chmiti et Ismail Haddaoui

**Enseignante :** Mme Soukaina Gouraguine

**Date :** 25 novembre 2026

## 1. Constat initial

Avant installation, l'import dans le projet affiche le fichier logiai/__init__.py.
Depuis son dossier parent, il échoue avec ModuleNotFoundError: No module named 'logiai'.
Pour utiliser LogiAI, mon collègue doit installer le package dans son environnement,
recevoir les artefacts du modèle et définir LOGIAI_HOME vers leur dossier.

La branche tp6 part d'atelier5 : main contient encore l'atelier 4 et la PR de
l'atelier 5 est toujours en attente de fusion. La PR tp6 cible donc atelier5.

## 2. Métadonnées et installation éditable

pyproject.toml declare logiai 0.1.0, setuptools, le moteur de prédiction, les extras
api et dev, ainsi que le point d'entree logiai-predict = logiai.cli:main.
python-dotenv est ajoute aux dépendances car config.py l'importe.
Avant installation : 2 échecs de métadonnées de package et 58 autres tests réussis.
Après pip install -e ".[api,dev]", l'import fonctionne depuis le dossier parent,
pointe vers le code source et la suite complete donne 60 passed.
Le CLI renvoie 1 pour un fichier absent ou un JSON invalide, avec un message sur stderr.

## 3. Commande et question des 500 mm

La prédiction est portee par Predictor.predict dans logiai/predict.py.
La commande appelle ce meme code sans serveur et affiche, pour livraison.json :

```text
Probabilite de retard : 73 % (ALERTE) - seuil : 0.4
```

Avec pluie_mm = 500, le CLI affiche 100 % (ALERTE), code de sortie 0.
L'API refuse cette valeur avec HTTP 422 : le schema Livraison impose pluie_mm <= 100.
Le CLI ne reutilise pas ce schema, pour rester utilisable sans installer FastAPI
ni Pydantic. Cette valeur hors domaine illustre une limite de validation du CLI,
pas une estimation métier fiable.

## 4. Wheel et essai du collègue

python -m build construit dist/logiai-0.1.0-py3-none-any.whl et une archive source.
Le wheel inspecte contient 15 fichiers : le code logiai et les métadonnées.
Aucun models/, data/, tests/ ni .env ne se trouve dans le wheel.
Ces exclusions concernent le wheel ; l'archive source peut contenir des tests.

L'environnement .venv_test est cree sans reutiliser les paquets de .venv.
Le wheel y est installe avec les contraintes de requirements-runtime.txt pour
conserver les versions compatibles avec le modèle existant. L'essai est effectue
depuis un dossier temporaire vide, sans PYTHONPATH ni installation éditable.

Sans LOGIAI_HOME : le CLI doit signaler le modèle absent du dossier courant.
Avec LOGIAI_HOME pointant vers le projet : la commande doit retrouver la prédiction.
Les messages observes sont enregistres dans les preuves de verification.
Essai effectivement réussi dans l’environnement neuf, sans FastAPI installé :

```text
Sans LOGIAI_HOME : code 1, Modèle introuvable : <dossier temporaire>/models/model.joblib.
Définissez LOGIAI_HOME vers le dossier contenant models/.
Avec LOGIAI_HOME : code 0, Probabilité de retard : 73 % (ALERTE) - seuil : 0.4
```

L’import du collègue pointe vers `.venv_test/Lib/site-packages/logiai/__init__.py`.
ROOT utilise maintenant LOGIAI_HOME, avec Path.cwd() en repli ; le dossier
d'installation du package n'est plus utilise comme répertoire d'artefacts.

## 5. Package dans Docker

Le Dockerfile installe les dépendances aux versions fixees, copie pyproject.toml
et logiai dans /tmp/build puis execute :

```dockerfile
RUN pip install --no-cache-dir --no-deps /tmp/build && rm -rf /tmp/build
```

Le dossier source temporaire est retire dans la meme couche. LOGIAI_HOME=/app
conserve les montages de données et modèle. /app ne doit plus contenir logiai.
Chemin observe dans le conteneur :
`/usr/local/lib/python3.12/site-packages/logiai/__init__.py`.
`ls /app` contient models, data et requirements-runtime.txt, sans logiai.
Le dossier /tmp/build est absent. L'API est healthy et les appels via Nginx
donnent 401 sans clé, 401 avec une fausse clé, 200 avec la bonne clé,
422 pour une entree invalide et 403 pour un role insuffisant.
Le cas pluie_mm = 500 a bien ete refuse avec 422 par l'API reconstruite.

## 6. Conception et remise

Pull request : https://github.com/mccrking/LogiAI/pull/2

L'ADR 005 justifie les bornes >= du package et les versions == du deploiement,
ainsi que le choix d'un modèle externe. L'etude de conception contient les neuf
rubriques demandees ; seule architecture est rédigée, avec un schema Mermaid.
Les comptes rendus precedents sont conserves dans docs/.

.env, dist/, build/, .venv/, .venv_test/ et les métadonnées egg-info sont ignores
par Git. Le wheel reste disponible localement pour la livraison au collègue.
La relecture par le binôme, la fusion et le tag tp6 restent a réaliser après
approbation reelle de la pull request.

## Ticket de sortie propose

- Docker empaquette aussi le systeme et l'environnement d'execution ; le package
  distribue une bibliotheque Python et ses points d'entree.
- Installation éditable pour developper ; wheel pour livrer une version construite.
- Le modèle, ses métadonnées, les données et les secrets ne sont pas dans le wheel.
  Fournir le modèle et ses métadonnées, les versions compatibles et LOGIAI_HOME.
- Point personnel a confirmer : approfondir la compatibilite des versions de
  scikit-learn avec les artefacts serialises avant transcription sur papier.
