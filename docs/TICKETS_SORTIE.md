# Tickets de sortie — Atelier 5

**Enseignante :** Mme Soukaina Gouraguine

**Date :** 11 novembre 2026

Ces réponses sont des propositions à relire et à transcrire individuellement
sur papier. Chaque étudiant doit ajouter son groupe et confirmer ou remplacer
la réponse personnelle à la question 4.

## Mehdi Chmiti

1. **Image et conteneur.** L’image contient le programme et ses dépendances.
   Le conteneur est une instance exécutée avec sa propre couche inscriptible.
2. **Chemin relatif.** `/api/v1/predict` reste sur l’origine de la page. Nginx
   relaie vers `api:8000`, nom connu dans Docker mais pas par le navigateur Windows.
3. **Disponibilité.** `depends_on` seul organise les démarrages ;
   `service_healthy` attend que l’API et son modèle soient prêts.
4. **Point personnel à confirmer.** Proposition : approfondir la gestion des
   clés et HTTPS pour un déploiement en production.

## Ismail Haddaoui

1. **Image et conteneur.** L’image sert de modèle ; le conteneur est le processus
   isolé qui l’exécute. Plusieurs conteneurs peuvent partager la même image.
2. **Chemin relatif.** Le navigateur contacte son propre hôte et son propre port.
   Nginx retire `/api/` et résout ensuite le nom du service interne `api`.
3. **Disponibilité.** Un conteneur démarré n’est pas forcément prêt.
   `service_healthy` attend la réussite du healthcheck avant de lancer le web.
4. **Point personnel à confirmer.** Proposition : approfondir la gestion des
   versions du modèle et la surveillance des conteneurs après démarrage.
