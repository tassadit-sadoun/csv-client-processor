## Pistes d'amélioration des tests API

Ces améliorations ont été identifiées mais non implémentées par manque de temps. Elles visent à renforcer la couverture des tests, la robustesse du système et la gestion des cas limites.

###  Tests sur l’import de fichiers CSV

- [ ] Ajouter un test avec un fichier mal formé (ex : en-têtes manquants, colonnes incorrectes).
- [ ] Ajouter un test avec un fichier d’un type incorrect (ex : `.txt`, `.json`) pour vérifier le filtrage MIME.
- [ ] Tester l'import d'un fichier très volumineux pour valider le comportement en cas de surcharge.

### Tests de sécurité

- [ ] Supprimer ou désactiver temporairement le mock de l’authentification (`fake_get_current_user`) pour tester les comportements réels liés aux tokens.
- [ ] Vérifier le comportement **sans jeton d’authentification** : une requête sans en-tête `Authorization` doit retourner un code 401.
- [ ] Vérifier le comportement **avec un jeton invalide ou expiré** : la route doit refuser l'accès avec un message d'erreur approprié.

### Tests des cas limites et erreurs

- [ ] Tester la route `/api/imports/{job_id}/status` avec un UUID invalide (format incorrect → 422 attendu).  
- [ ] Tester `/api/clients` sans pagination pour valider le fallback aux valeurs par défaut.
- [ ] Ajouter un test sur une route inexistante pour vérifier la gestion des 404.
       



## Améliorations possibles des tests de la tâche d’import

Ces pistes d'amélioration visent à renforcer la robustesse des tests liés à la tâche `run_import_job` et à la fonction `process_csv`. Faute de temps, elles n'ont pas été mises en place, mais elles seraient prioritaires dans un contexte de production.

### Cas fonctionnels et de validation

- [ ] Import de fichiers CSV vides, sans aucune ligne à traiter.
- [ ] Fichiers CSV composés uniquement de lignes invalides (échec total de validation).
- [ ] Données contenant des dates malformées, absentes ou incorrectes.
- [ ] Lignes avec des champs manquants ou vides (ex. email absent).
- [ ] CSV avec des doublons ou incohérences logiques (même email pour plusieurs lignes).
👉 Actuellement, **aucune logique de détection ou de rejet des doublons ou encodage inhabituel dans les données etc** (par exemple sur l'email) n'est implémentée.  
      Il serait pertinent d’ajouter une **vérification coté schéma/model** pour éviter l’insertion de clients identiques ou données avec accents, emojis par exemple.

### Tests de performance et scalabilité

- [ ] Gestion de très gros fichiers CSV pour tester la montée en charge.
- [ ] Évaluer la consommation mémoire / temps de traitement sur des volumes élevés.

### Cas d’erreurs techniques

- [ ] Cas où la connexion à la base de données échoue ou la session n’est pas accessible.
- [ ] Scénarios où la tâche Celery dépasse le nombre maximal de retries autorisés.
- [ ] Gestion des erreurs inattendues lors du traitement du CSV (ex. crash Pydantic, encodage).

### Tests d’intégration

- [ ] Ajouter des tests d’intégration réels exécutant la fonction `process_csv` sur de vrais fichiers CSV et une base de données de test (sans mocks), afin de valider le comportement complet en environnement réel.


### Améliorations possibles des modèles (`models.py`)

- [ ] Ajouter une contrainte d’unicité sur `Client.email` pour éviter les doublons côté base de données.  
      👉 Actuellement, aucun contrôle ne garantit qu’un même email ne soit pas inséré plusieurs fois.

- [ ] Ajouter un champ `import_job_id` (clé étrangère) dans `Client` pour tracer l’origine d’un enregistrement.  
      👉 Cela permettrait de lier chaque client à l’import correspondant pour faciliter l’audit.

- [ ] Ajouter un index composite sur (`email`, `birth_date`) si ces champs sont utilisés fréquemment pour des recherches combinées.  

- [ ] Ajouter des contraintes au niveau des champs :  
  - `String(length)` au lieu de `String` sans taille (par exemple `String(255)` pour `email`)  

- [ ] Dans `ImportJob` :  
  - Ajouter un champ `filename` (ou `source`) pour garder une trace du fichier CSV utilisé.  
  - Permettre un champ `error_log` (texte ou JSON) pour stocker les lignes rejetées ou les erreurs précises détectées.

### Améliorations possibles des api/crud/base.py

- [ ] Ajouter des méthodes `update` et `delete` pour compléter les opérations CRUD.  
      👉 La classe actuelle respecte le périmètre demandé (Create et Read uniquement),  
      mais resterait incomplète dans un contexte CRUD général.

### Améliorations possibles des schémas Pydantic

- [ ] Ajouter des contraintes de validation supplémentaires dans `ClientSchema`, comme :  
  - `name`: longueur minimale/maximale (`min_length`, `max_length`)  
  - `birth_date`: validation personnalisée pour interdire les dates futures

### Améliorations des schémas et validations

- [ ] Ajouter un validateur pour interdire les dates de naissance futures.
- [ ] Vérifier que le champ `name` n'est pas vide ou uniquement composé d'espaces.
- [ ] Afficher des messages d'erreur personnalisés pour les emails invalides.
- [ ] Ajouter un validateur racine pour détecter des incohérences multi-champs.
- [ ] Ajouter des tests de validation sur des entrées clairement invalides.
- [ ] Uniformiser l’utilisation de `EmailStr` (utilisé dans `ClientSchema`, mais pas dans `ClientResponse`)  
      👉 Cela permettrait de garder une validation forte même en sortie.

### Améliorations de l’authentification/ Securité

- [ ] Ajouter un provider de gestion des identifiants (`CredentialProvider`) pour centraliser la logique d’accès aux `client_id` et `client_secret` (ex. depuis un fichier, une base de données ou un gestionnaire de secrets).
- [ ] Gérer l’expiration des tokens côté client en ajoutant un mécanisme de **renouvellement périodique** via un endpoint `/refresh_token`.
- [ ] Implémenter un système de **permissions** et de **rôles** dans les tokens JWT (ex. `"role": "admin"`, `"scopes": ["read", "write"]`) pour une gestion plus fine de l’accès aux routes.
- [ ] Logger toutes les tentatives d’authentification, réussies ou échouées, avec le `client_id` et l’IP (sans journaliser les secrets).
- [ ] Ajouter des tests automatisés couvrant les cas :
  - Absence du header `Authorization`
  - Format invalide du token
  - Expiration du token
  - Tentative avec des credentials invalides
  - Accès à une route protégée sans le bon rôle ou scope

### Améliorations Securité Limitation de débit (Throttling)

- [ ] Implémenter une limitation de débit globale sur les endpoints sensibles (ex: `/access_token`, `/import`) pour éviter les abus.
- [ ] Implémenter un système de throttling qui reconnaît le rôle de l’utilisateur ex. `"role": "admin"` à partir du token JWT.
- [ ] Retourner une erreur 429 (`Too Many Requests`) lorsque la limite est atteinte.
- [ ] Ajouter des en-têtes HTTP pour informer le client :
  - `X-RateLimit-Limit`: nombre max autorisé
  - `X-RateLimit-Remaining`: combien de requêtes restantes
  - `Retry-After`: temps à attendre avant de retenter

### Caching avec Redis

- [ ] Mettre en place un cache Redis pour améliorer les performances des endpoints fréquents.
- [ ] Éviter de mettre en cache les données sensibles ou personnelles  notamment les informations clients (`email`, `birth_date`), pour respecter la confidentialité et les règles de sécurité.
- [ ] Prévoir un mécanisme d’invalidation du cache en cas de modification des données sous-jacentes (signal).


# Notification email via signal après traitement CSV

## Description  
- [ ] Mettre en place un **signal** (ou un système d’événement) qui se déclenche une fois que la tâche d’import CSV est terminée.
- [ ] Ce signal appellera une fonction responsable d’envoyer un email de notification au(x) destinataire(s).

## Détails  
- [ ] Définir un signal `import_completed`
- [ ] Émettre ce signal à la fin de la fonction/tâche de traitement CSV, en passant un résumé du traitement.  
- [ ] Connecter un handler au signal qui envoie l’email de notification.  
- [ ] Cette approche découple le traitement CSV et la notification, facilitant la maintenance