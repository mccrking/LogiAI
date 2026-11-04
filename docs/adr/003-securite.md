# ADR 003 : sécurité de l'API LogiAI

## Décision 1 : transmettre la clé dans un en-tête

La clé est envoyée dans `X-API-Key`, jamais dans l'URL ni dans le corps JSON.
Une clé dans l'URL se retrouverait plus facilement dans l'historique du navigateur,
les journaux et les outils de supervision. Une clé dans le corps imposerait un
contrat différent selon les endpoints et pourrait être enregistrée avec les données
métiers.

## Décision 2 : autoriser une liste précise d'origines

La seule origine autorisée est `http://localhost:5500`. Utiliser `*` permettrait à
n'importe quelle page web de lire les réponses dans le navigateur et empêcherait
une politique CORS restrictive. La clé API reste nécessaire : CORS ne protège pas
les appels directs comme ceux effectués avec curl.
