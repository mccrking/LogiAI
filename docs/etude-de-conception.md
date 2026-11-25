# Étude de conception de LogiAI

## Besoin

## Données

## Modèle et métriques

## Critères d’acceptation

## Cycle de vie

## Architecture

```mermaid
flowchart LR
    D[Livraisons CSV] --> T[Entraînement via le package logiai]
    T --> M[Modèle joblib et métadonnées externes]
    subgraph APIContainer[Conteneur API Python]
        A[API FastAPI] --> P[Package logiai installé dans site-packages]
    end
    subgraph WebContainer[Conteneur web Nginx]
        N[Nginx reverse proxy]
        W[Page web statique]
        N --> W
    end
    B[Navigateur] --> N
    N -->|/api/ vers api:8000| A
    M -->|Montage lecture seule| P
    C[Commande logiai-predict] --> P
    J[Fichier livraison JSON] --> C
    B -->|Saisie livraison et clé| W
    P --> R[Probabilité et alerte]
```

Le même package porte le chargement et l’inférence pour le CLI et l’API.
Le CLI fonctionne sans installer l’extra API. FastAPI apporte sa validation et
son contrôle d’accès ; Nginx sert la page et relaie les requêtes sur une origine
unique. Compose coordonne les deux conteneurs. Le modèle et les données restent
externes au wheel ; `LOGIAI_HOME` désigne leur répertoire. L’entraînement est
une étape explicite du cycle de vie, jamais exécutée par une requête de prédiction.

## Choix technologiques

## Risques et éthique

## Limites
