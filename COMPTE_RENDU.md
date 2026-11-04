# Compte rendu : TP sécurité LogiAI

**Noms :** ............................  **Groupe :** ........

## 1. Environnement et premiers tests
- Le starter a été complété dans un environnement virtuel Python.
- Les tests de validation retournent 422 grâce à Pydantic, avant l'implémentation
  de la prédiction.
- Après l'implémentation, la suite complète passe : **52 passed**.

## 2. Mon schéma
- Les bornes sont contrôlées par les champs `Field` de `logiai/api/schemas.py`.

| Variable | Min | Max | Pourquoi |
|---|---|---|---|
| distance_km | 1 | 1000 | trajet logistique réaliste |
| poids_kg | 0.1 | 5000 | charge positive et compatible avec un camion |
| heure_depart | 0 | 23 | heure d'une journée |
| pluie_mm | 0 | 100 | pluie non négative, plafond réaliste |
| trafic_index | 0 | 10 | échelle fluide à saturée |
| nb_arrets | 0 | 50 | nombre d'arrêts entier et borné |

## 3. Sécurité
- `X-API-Key` est comparée avec `secrets.compare_digest`.
- Une clé absente ou fausse donne 401.
- Une clé utilisateur sur `/v1/model-info` donne 403 ; la clé administrateur
  donne 200.
- `/health` reste public.
- Le modèle, les clés et le CSV généré ne sont pas suivis par Git.

## 4. Quatre requêtes
| Requête | Code obtenu | Pourquoi |
|---|---|---|
| livraison normale avec clé utilisateur | 200 | schéma valide et modèle chargé |
| distance_km = -5 | 422 | borne Pydantic dépassée |
| type_vehicule = "avion" | 422 | valeur absente du `Literal` |
| modèle absent | 503 | service temporairement indisponible |

## 5. Questions de compréhension
1. Le modèle est chargé au démarrage pour éviter un coût à chaque requête.
2. Pydantic écrit le contrôle `pluie <= 100` dans `schemas.py`.
3. 422 signifie données invalides ; 503 signifie modèle indisponible.
4. `/v1/predict` permet de versionner le contrat de l'API.
5. Une distance décimale serait rejetée si elle était déclarée `int`.

## 6. Décision : modèle absent
LogiAI répond 503 : l'API reste joignable pour la supervision, mais aucune
prédiction n'est servie tant que le modèle n'est pas disponible.

## 7. Client web et CORS
- `web/index.html` appelle l'API en POST avec `Content-Type` et `X-API-Key`.
- Seule l'origine `http://localhost:5500` est autorisée.
- Le port 5501 est refusé par le navigateur, tandis que curl fonctionne car CORS
  est un contrôle du navigateur et non une authentification serveur.

## 8. Lien de la pull request
