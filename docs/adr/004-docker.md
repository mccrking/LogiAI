# ADR 004 — Conteneuriser LogiAI avec Docker et Nginx

Date : 11 novembre 2026. Statut : mis en œuvre sur la branche `atelier5`.

## Contexte

L’API FastAPI et la page de l’atelier 4 doivent fonctionner dans deux conteneurs,
avec un démarrage coordonné par Compose. La page utilise `/api/v1/predict` :
Nginx transmet `/v1/predict` à `api:8000`, sur le réseau privé de Compose.
La clé `X-API-Key` est conservée par le proxy. Ce proxy ne remplace pas
l’authentification et ne masque pas une clé saisie dans le navigateur.

## Décision 1 — Une copie dans l’image et des montages en lecture seule

Le Dockerfile copie `data/` et `models/` pour permettre l’activité avec une image
API autonome. Compose monte ensuite `./data:/app/data:ro` et
`./models:/app/models:ro`. Les montages masquent les copies intégrées à l’image.
L’API n’a besoin que de lire ces fichiers.

Un modèle réentraîné sur l’hôte est visible dans le conteneur sans reconstruire
l’image. Il faut toutefois redémarrer l’API, car Predictor charge le modèle une
seule fois au démarrage. Un changement du code, copié dans l’image et non monté,
nécessite une reconstruction. L’alternative COPY seule rendrait l’image plus
autonome mais imposerait une reconstruction à chaque changement de modèle.
L’alternative volume seul empêcherait de lancer l’image autonome sans artefacts
externes. Les versions des dépendances principales, notamment scikit-learn,
sont fixées pour garder le chargement du modèle cohérent entre hôte et image.

Les artefacts restent exclus de Git. Un nouveau clone doit donc les générer avant
le build final. L’étape Docker `trainer` et `scripts/prepare-model.ps1` permettent
cette préparation sur Windows sans installer Python sur l’hôte. Cet entraînement
est explicite ; l’API ne réentraîne jamais son modèle au démarrage.

## Décision 2 — Publier 8080 et 8001 pour l’atelier

Compose publie `127.0.0.1:8080:80` pour la page et
`127.0.0.1:8001:8000` pour l’API et Swagger. Cette configuration répond aux essais
du sujet et évite le port 8000 utilisé pendant l’atelier 4. La publication est
limitée à la machine locale ; le réseau interne joint toujours `api:8000`.

Pour une présentation sur le réseau local, `LOGIAI_WEB_BIND=0.0.0.0` dans le
`.env` local ouvre uniquement la publication du service web à toutes les
interfaces. La valeur par défaut reste `127.0.0.1`, et le port API 8001 reste
limité au PC. Le pare-feu et l’isolation éventuelle du Wi-Fi conditionnent
l’accès depuis une autre machine ; cette option ne crée pas d’accès Internet.

Le port 8001 permet de contourner Nginx, mais pas la vérification de clé de
FastAPI. Il faudrait reproduire les éventuelles protections de Nginx sur ce
chemin direct. Ne publier que 8080 réduirait les points d’entrée ; cela ferait
perdre l’accès direct de diagnostic sur 8001. Swagger reste utilisable via
`http://localhost:8080/api/docs`, qui charge son schéma par un chemin relatif.

## Préparation et limites

Le healthcheck vérifie à la fois une réponse HTTP et `model_loaded: true`.
`condition: service_healthy` attend cette disponibilité avant le démarrage du web.
Cette dépendance ne garantit pas la disponibilité permanente : une panne
ultérieure de l’API produit un 502 Nginx, traité explicitement par la page.

Python 3.12 remplace l’exemple 3.11 du sujet pour conserver la version du projet
et de son environnement d’entraînement. Les dépendances de test sont séparées
de celles d’exécution ; l’API s’exécute avec l’UID 10001. `.env` et ses variantes
sont exclus du contexte Docker et de Git. Les secrets sont fournis à l’exécution.

Cette pile est une démonstration locale : pas de terminaison TLS, de rotation
automatique des clés, de limitation de débit, de supervision durable ni de haute
disponibilité. Nginx et Python utilisent des tags versionnés par famille, mais
leurs images et les dépendances transitives ne sont pas figées par digest ou
fichier de verrouillage complet. Une publication en production nécessiterait
ces décisions supplémentaires et une validation du modèle sur des données réelles.
