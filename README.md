# Service de traitement asynchrone de fichiers CSV clients

Vous devez concevoir un petit service de traitement asynchrone de fichiers CSV clients.  
L’objectif est de démontrer votre maîtrise de Python, Celery, Redis et PostgreSQL, ainsi que vos bonnes pratiques.

---

## Enoncé du projet

### Objectifs du test

1. **API RESTful pour :**  
   - Upload d’un fichier CSV contenant des enregistrements « client » (nom, email, date de naissance).  
   - Consultation du statut d’un traitement (en file, en cours, terminé, échoué).  
   - Récupération des données traitées paginées.

2. **Traitement asynchrone :**  
   - Dès réception du CSV, lancer un worker Celery qui :  
     - Parse le fichier, valide chaque ligne (email valide, date au format ISO).  
     - Insère en base PostgreSQL les enregistrements valides, marque les lignes invalides en erreur avec message associé.

3. **Base PostgreSQL :**  
   - Modéliser une table `clients` et une table `import_jobs` (statut, timestamps, nb lignes totales/validées/erronées).  
   - Indexer les colonnes les plus utilisées (email, date de naissance).

4. **Tests :**  
   - Écrire des tests unitaires pour l’API et le worker (pytest).

---

## Consignes détaillées

- **Stack choisi :** Python 3.13.0, Pydantic, FastAPI, Celery, PostgreSQL.  
- **Broker :** Redis (via Docker-Compose).  
- **ORM :** SQLAlchemy.  
- **Livrables :**  
  1. Le code source (public Git ou archive).  
  2. Un `docker-compose.yml` qui lance :  
     - L’API (`app`)  
     - Redis

---

## Critères d’évaluation

| Domaine        | À vérifier                                              |
|----------------|----------------------------------------------------------|
| Fonctionnalité | Endpoints conformes, traitement asynchrone              |
| Qualité du code| Lisibilité, modularité, respect des conventions       |
| Tests          | Couverture, cas succès/échec, fixtures                  |
| Base de données| Modèles cohérents, indexation, migrations               |
| Performance & fiabilité | Gestion des erreurs, reprise sur échec     |
| Documentation  | Clarté, instructions reproductibles                   |

---
## Bonus (optionnels)

- Système de notifications (email ou webhook) lorsque le job est terminé
- Gestion du cache avec Redis
- Sécuriser les endpoints


## Lancer le projet

Assurez-vous d'avoir Docker et Docker Compose installés.

### 1. Lancer les conteneurs

```bash
docker compose up --build
docker compose up
```

### 2. Appliquer les migrations (création des tables)

Les fichiers de migration sont déjà présents dans le projet (`migrations/` est versionné). Il suffit d'appliquer les migrations :

```bash
docker compose exec app alembic upgrade head
```

---

## Tester l’API

### 1. Authentification (client credentials)

```bash
curl -X POST http://localhost:8000/auth/access_token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=UezjwqiRG6cKJRtSdTBjrkLI09HpWPxDLdweOisr&client_secret=V5tSsR9VSWISVamUl8KweBiydAZ2SKV7Rs4NqZIeTQBB42IMrAGB1SRpoJpmIvEdcKQaGjrt6XLvRmwcUnqWV5CzO7ReHHHWS1x5GwxvxOI6tq87HpV8DlZZStGqZGUL"
```

### 2. Import de fichier CSV

```bash
curl -F "file=@clients_utf8.csv" http://localhost:8000/api/imports \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJVZXpqd3FpUkc2Y0tKUnRTZFRCanJrTEkwOUhwV1B4RExkd2VPaXNyIiwiZXhwIjoxNzc5NzEzNzE5LCJpYXQiOjE3NDgxNzc3MTl9.w5E64b78xLpjLEXuTt9CzYtJKlgomaQO_RrLi2_Edz8"
  # → {"job_id":"e652107a-2be1-4d20-8846-1f426e3341aa","status":"pending"}
```

### 3. Liste des clients importés

```bash
curl "http://localhost:8000/api/clients?page=1&per_page=20" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJVZXpqd3FpUkc2Y0tKUnRTZFRCanJrTEkwOUhwV1B4RExkd2VPaXNyIiwiZXhwIjoxNzc5NzEzNzE5LCJpYXQiOjE3NDgxNzc3MTl9.w5E64b78xLpjLEXuTt9CzYtJKlgomaQO_RrLi2_Edz8"
  # → {"clients":[...],"page":1,"total_pages":3}
```

### 4. Suivi du statut d’un job d’import

```bash
curl http://localhost:8000/api/imports/e559be95-fb8e-4114-b256-9ff081267f52/status \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJVZXpqd3FpUkc2Y0tKUnRTZFRCanJrTEkwOUhwV1B4RExkd2VPaXNyIiwiZXhwIjoxNzc5NzEzNzE5LCJpYXQiOjE3NDgxNzc3MTl9.w5E64b78xLpjLEXuTt9CzYtJKlgomaQO_RrLi2_Edz8"
  # → {"job_id":"e559be95-fb8e-4114-b256-9ff081267f52","status":"COMPLETED","total":10,"valid":10,"errors":0}
```

---

## Lancer les tests

```bash
docker exec app_container env PYTHONPATH=/usr/src/app pytest -v tests
```

---

## Autres commandes utiles

### Arrêter les conteneurs

```bash
docker compose down
```

### Générer une nouvelle migration (si changement des modèles SQLAlchemy)

```bash
docker compose exec app alembic revision --autogenerate -m "votre message ici"
docker compose exec app alembic upgrade head
```

---

## Permissions sous WSL2 / Linux

Si vous rencontrez des erreurs de type `EACCES` (permission denied) :

```bash
sudo chown -R $(whoami):$(whoami) migrations/
chmod -R u+rw migrations/
```

---

## Consulter la base de données (PostgreSQL)

```bash
docker exec -it database_container psql -U user -d alpha
```

Dans `psql` :

```sql
SELECT * FROM import_jobs;
SELECT * FROM clients;
```

---

## Structure du projet

```
csv-client-processor/
│
├── README.md
├── alembic.ini
├── docker-compose.yml
├── pyrightconfig.json
├── clients_utf8.csv
│
└── api/                        # Dossier principal de l'application FastAPI
    ├── Dockerfile
    ├── main.py                 # Point d'entrée de l’application FastAPI
    ├── alembic.ini
    ├── tasks.py                # Tâches Celery
    ├── crud/                  # Fonctions de manipulation DB (Create, Read)
    ├── database/              # Connexion et configuration de la base de données
    ├── log_config/            # Configuration des logs (LOGGING_CONFIG)
    ├── migrations/            # Dossier de migration Alembic
    ├── models/                # Modèles SQLAlchemy
    ├── routers/               # Fichiers de routing FastAPI (endpoints)
    ├── schemas/               # Schémas Pydantic pour validation et sérialisation
    ├── security/              # Authentification
    ├── services/              # Logique métier (traitements CSV)
    └── tests/                 # Tests
```

---

## Notes

- N'oubliez pas d’adapter les tokens JWT et les identifiants à vos propres valeurs.
- Les migrations étant versionnées, la première application (`alembic upgrade head`) suffit pour créer toutes les tables.
- Le fichier `.env` est inclus pour faciliter les tests locaux et garantir une exécution immédiate du projet en environnement de développement.
