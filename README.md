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

## Exemple de scénario de test rapide

```bash  
# Upload du fichier CSV  
curl -F "file=@clients.csv" http://localhost:8000/api/imports  
# → { "job_id": "abc123", "status": "PENDING" }  

# Vérifier le statut du traitement  
curl http://localhost:8000/api/imports/abc123/status  
# → { "job_id": "abc123", "status": "SUCCESS", "total": 50, "valid": 48, "errors": 2 }  

# Récupérer la liste des clients  
curl http://localhost:8000/api/clients?page=1&per_page=20  
# → { "clients": [ … ], "page":1, "total_pages":3 }  

## Bonus (optionnels)

- Système de notifications (email ou webhook) lorsque le job est terminé
- Gestion du cache avec Redis
- Sécuriser les endpoints