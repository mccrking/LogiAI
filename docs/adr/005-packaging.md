# ADR 005 - Packaging de LogiAI

Date : 25 novembre 2026. Statut : mis en œuvre sur `tp6`.
Le package `logiai` version 0.1.0 expose une bibliothèque et `logiai-predict`.
`pyproject.toml` utilise des bornes `>=` pour annoncer les versions compatibles.
Cela laisse l’installateur résoudre les dépendances dans l’environnement du collègue.
Des versions `==` ici imposeraient inutilement notre environnement à chaque utilisateur.
`requirements-runtime.txt`, inclus par `requirements.txt`, fixe les versions `==` déployées.
Des bornes ouvertes seules en déploiement rendraient le chargement du modèle moins reproductible.
Le wheel contient uniquement le code et les métadonnées, sans données, modèle ni secrets.
Embarquer le modèle faciliterait un essai isolé mais couplerait chaque entraînement à une version du package.
Les artefacts restent dans `models/` et `data/`, désignés par `LOGIAI_HOME`, ou le dossier courant en repli.
Le collègue doit recevoir le modèle et ses métadonnées compatibles en plus du wheel ; Docker fournit aussi l’environnement d’exécution.
