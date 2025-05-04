# Baby Foot ELO

## Description

Le baby-foot, également connu sous le nom de football de table, est un jeu de société où deux équipes de deux joueurs manipulent des figurines fixées sur des barres pour frapper une petite balle et tenter de marquer des buts dans le camp adverse. Au baby-foot, le terme "fanny" désigne une situation où une équipe termine une partie avec un score de zéro.

Baby Foot ELO est une application web qui permet à un groupe d'individus (collègues, amis, etc.) de suivre un championnat de baby-foot. Sa particularité réside dans l'utilisation d'un système de classement ELO hybride, où les joueurs d'une même équipe ne gagnent ou ne perdent pas le même nombre de points. Le calcul des points est personnalisé en fonction du classement individuel de chaque joueur et du classement de l'équipe adverse, offrant ainsi une évaluation plus juste des performances individuelles.

## Fonctionnalités

### Gestion des joueurs

- Enregistrement de nouveaux joueurs avec profil personnalisé
- Attribution d'un ELO initial (par défaut: 1000)
- Visualisation des statistiques individuelles
- Suivi de l'évolution de l'ELO au fil du temps

### Gestion des équipes

- Formation d'équipes de deux joueurs
- Suggestion automatique des paires d'équipes possibles à partir des joueurs enregistrés
- Calcul de l'ELO d'équipe (basé sur les ELO individuels, calculé dynamiquement)
- Classement dynamique des équipes (basé sur l'ELO d'équipe calculé)

### Gestion des matchs

- Enregistrement des résultats de matchs (vainqueur, perdant, score)
- Support pour les matchs "fanny" (symbolique, sans impact sur l'ELO)
- Calcul automatique des points ELO gagnés/perdus
- Historique complet des matchs joués

### Statistiques et visualisations

- Tableaux de classement des joueurs par ELO
- Tableaux de classement des équipes par ELO
- Graphiques d'évolution de l'ELO dans le temps
- Statistiques de compatibilité entre joueurs (taux de victoire par paire)
- Filtrage des classements par période (année, mois)

### Exports et data

- Export des résultats des matchs en JSON
- Historique complet consultable
- Données persistantes pour le suivi à long terme

## Architecture Technique

### Frontend

- Framework: **Next.js**
  - Interface réactive et moderne
  - Routage basé sur le système de fichiers
  - Thème sombre/clair avec dominante vert islamique
  - Composants réutilisables pour les tableaux et graphiques

### Backend

- Framework: **FastAPI**
- Framework web Python moderne et performant pour construire des APIs.
- Validation automatique des données grâce à Pydantic.
- Documentation API interactive générée automatiquement (Swagger UI, ReDoc).
- Support asynchrone pour des opérations I/O non bloquantes.

### Base de Données

- Système: **DuckDB**
- Base de données analytique in-process.
- Stockage des données dans un fichier unique (`.duckdb`).
- Syntaxe SQL standard, facilitant les requêtes complexes.
- Adaptée pour des applications où la base de données peut être locale au serveur backend.

### Modèle de données

*(Note: Le modèle est défini pour être utilisé avec DuckDB via SQLAlchemy ou un ORM similaire dans FastAPI. Les types de données sont indicatifs et peuvent être adaptés.)*

- **Joueurs**: `id` (INTEGER PRIMARY KEY), `nom` (VARCHAR), `elo` (INTEGER), `date_creation` (TIMESTAMP)
- **Equipes**: `id` (INTEGER PRIMARY KEY), `joueur1_id` (INTEGER REFERENCES Joueurs), `joueur2_id` (INTEGER REFERENCES Joueurs), `dernier_match` (TIMESTAMP) *(Note: Représente une paire unique de joueurs ayant joué ensemble. L'ELO d'équipe est calculé dynamiquement.)*
- **Matchs**: `id` (INTEGER PRIMARY KEY), `équipe_gagnante_id` (INTEGER REFERENCES Équipes), `équipe_perdante_id` (INTEGER REFERENCES Équipes), `score_gagnant` (INTEGER), `score_perdant` (INTEGER), `est_fanny` (BOOLEAN), `date` (TIMESTAMP), `année` (INTEGER), `mois` (INTEGER)
- **Historique_ELO**: `id` (INTEGER PRIMARY KEY), `joueur_id` (INTEGER REFERENCES Joueurs), `match_id` (INTEGER REFERENCES Matchs), `ancien_elo` (INTEGER), `nouvel_elo` (INTEGER), `difference` (INTEGER), `date` (TIMESTAMP), `année` (INTEGER), `mois` (INTEGER)
- **Classements_Périodiques**: `id` (INTEGER PRIMARY KEY), `joueur_id` (INTEGER REFERENCES Joueurs), `année` (INTEGER), `mois` (INTEGER), `elo` (INTEGER), `position` (INTEGER), `matchs_joues` (INTEGER), `victoires` (INTEGER), `défaites` (INTEGER) *(Note: Stocke les classements périodiques des JOUEURS.)*
- **Classements_Equipes_Periodiques**: `id` (INTEGER PRIMARY KEY), `equipe_id` (INTEGER REFERENCES Équipes), `année` (INTEGER), `mois` (INTEGER), `elo_moyen` (FLOAT), `position` (INTEGER), `matchs_joues` (INTEGER), `victoires` (INTEGER), `défaites` (INTEGER) *(Note: Stocke les classements périodiques des ÉQUIPES.)*

#### Diagramme Entité-Relation (Conceptuel)

```mermaid
erDiagram
    JOUEURS ||--o{ HISTORIQUE_ELO : "tracks changes for"
    JOUEURS ||--o{ CLASSEMENTS_PERIODIQUES : "ranks"
    JOUEURS }o--|| EQUIPES : "forms (joueur1)"
    JOUEURS }o--|| EQUIPES : "forms (joueur2)"

    EQUIPES ||--o{ MATCHS : "wins"
    EQUIPES ||--o{ MATCHS : "loses"
    EQUIPES ||--o{ CLASSEMENTS_EQUIPES_PERIODIQUES : "ranks"

    MATCHS ||--|{ HISTORIQUE_ELO : "results in"

    JOUEURS {
        INTEGER id PK
        VARCHAR nom
        INTEGER elo
        TIMESTAMP date_creation
    }

    EQUIPES {
        INTEGER id PK
        INTEGER joueur1_id FK
        INTEGER joueur2_id FK
        TIMESTAMP dernier_match
    }

    MATCHS {
        INTEGER id PK
        INTEGER equipe_gagnante_id FK
        INTEGER equipe_perdante_id FK
        INTEGER score_gagnant
        INTEGER score_perdant
        BOOLEAN est_fanny
        TIMESTAMP date
        INTEGER annee
        INTEGER mois
    }

    HISTORIQUE_ELO {
        INTEGER id PK
        INTEGER joueur_id FK
        INTEGER match_id FK
        INTEGER ancien_elo
        INTEGER nouvel_elo
        INTEGER difference
        TIMESTAMP date
        INTEGER annee
        INTEGER mois
    }

    CLASSEMENTS_PERIODIQUES {
        INTEGER id PK
        INTEGER joueur_id FK
        INTEGER annee
        INTEGER mois
        INTEGER elo
        INTEGER position
        INTEGER matchs_joues
        INTEGER victoires
        INTEGER defaites
    }

    CLASSEMENTS_EQUIPES_PERIODIQUES {
        INTEGER id PK
        INTEGER equipe_id FK
        INTEGER annee
        INTEGER mois
        FLOAT elo_moyen
        INTEGER position
        INTEGER matchs_joues
        INTEGER victoires
        INTEGER defaites
    }
```

## Pages et interfaces

### Page d'accueil

![page d'accueil](./capture/home_page.png)
![template page d'accueil](./capture/template_homepage.png)

**Fonctionnalités:**

- Header avec navigation principale et switch thème clair/sombre
- Sélecteur de période pour les classements:
  - Option "Tous les temps" (vue par défaut)
  - Sélection par année (ex: 2025)
  - Sélection par mois (ex: Janvier 2025)
- Tableau de classement des joueurs par ELO
  - Position
  - Nom du joueur
  - Score ELO pour la période sélectionnée
  - Évolution sur la période (ou 7 derniers jours pour "Tous les temps")
  - Nombre de matchs joués dans la période
- Tableau de classement des équipes par ELO
  - Position
  - Noms des joueurs de l'équipe
  - Score ELO de l'équipe pour la période sélectionnée
  - Ratio victoires/défaites dans la période
  - Nombre de matchs joués ensemble dans la période
- Filtres additionnels:
  - Nombre minimum de matchs joués
  - Options d'affichage personnalisées
- Accès rapide aux pages joueur via les entrées du tableau

### Page d'information d'un joueur

![page d'information d'un joueur](./capture/template_player.png)

**Fonctionnalités:**

- Informations générales du joueur
  - Nom
  - ELO actuel
  - Date d'inscription
  - Nombre total de matchs
  - Ratio victoires/défaites
- Graphique d'évolution de l'ELO dans le temps
  - Visualisation claire de la progression
  - Points représentant les matchs joués
  - Informations détaillées au survol
  - Pas de filtrage possible
- Historique des matchs récents
  - Date et équipes
  - Score
  - Points ELO gagnés/perdus
  - Indication des "fanny"
- Statistiques de compatibilité
  - Tableau des partenaires préférentiels
  - Taux de victoire avec chaque partenaire
  - Nombre de matchs joués ensemble
  - ELO moyen de l'équipe formée
- Historique des classements par période:
  - Position et ELO par mois
  - Progression mensuelle visualisée

### Page des résultats et enregistrement de match

![page des résultats](./capture/add_match.png)

**Fonctionnalités:**

- Formulaire d'enregistrement de match
  - Sélection des joueurs pour chaque équipe
  - Interface intuitive pour former les équipes
  - Saisie des scores
  - Option "fanny" à cocher
  - Calcul en temps réel des points ELO potentiels (via appel API au backend)
  - Date du match (défaut: actuelle)
- Historique complet des matchs
  - Filtrable par joueur, équipe ou période (année, mois)
  - Tri par date, importance du match (points ELO échangés)
  - Détails complets accessibles
- Bouton d'export en JSON (via endpoint API backend)
  - Possibilité de sélectionner les matchs à exporter
  - Format structuré pour utilisation externe
- Statistiques globales
  - Nombre total de matchs
  - Moyenne de points par match
  - Répartition des "fanny"
  - Statistiques par période (année, mois)

### Page de gestion des joueurs

![page de gestion des joueurs](./capture/add_player.png)

**Fonctionnalités:**

- Formulaire d'ajout de nouveau joueur
  - Champ pour le nom
  - ELO initial (pas modifiable, défaut 1000)
- Liste des joueurs existants
  - Fonctionnalités de recherche et tri
  - Option de modification/désactivation
  - Statistiques résumées
- Outil de génération d'équipes
  - Suggestion d'équipes équilibrées (logique potentiellement côté backend)
  - Basé sur l'ELO ou d'autres critères
  - Utile pour organiser des matchs équitables
- Interface d'administration
  - Ajustements manuels d'ELO (via endpoint API sécurisé)
  - Fusion de profils en cas de doublon
  - Réinitialisation de saison

## Système ELO hybride

### Principe fondamental

Le système ELO hybride utilisé par Baby Foot ELO repose sur le principe que les joueurs d'une même équipe peuvent avoir des contributions différentes à la victoire ou la défaite. Ainsi, ils ne reçoivent pas nécessairement le même nombre de points après un match.

### Calcul détaillé

1. **Score ELO d'équipe**
   - Calculé comme la moyenne des ELO individuels des deux joueurs
   - Exemple: Équipe A (Joueur A1: 1200, Joueur A2: 800) = ELO équipe 1000

2. **Probabilité de victoire d'équipe**
   - P(A) = 1 / (1 + 10^((ELO_B - ELO_A) / 400))
   - Où ELO_A et ELO_B sont les scores ELO des équipes

3. **Facteur K individuel**
   - Varie selon l'ELO du joueur:
     - ELO < 1200: K = 100 (joueurs débutants, progression rapide)
     - 1200 ≤ ELO < 1800: K = 50 (joueurs intermédiaires)
     - ELO ≥ 1800: K = 24 (joueurs expérimentés, stabilité)

4. **Ajustement d'ELO individuel**
   - Pour une victoire:
     - Delta_ELO_i = K_i * (1 - P(équipe du joueur))
   - Pour une défaite:
     - Delta_ELO_i = K_i * (0 - P(équipe du joueur))

### Exemple concret

- **Équipe A**: Joueurs A1 (ELO 1200) et A2 (ELO 1000) → ELO équipe = 1100
- **Équipe B**: Joueurs B1 (ELO 900) et B2 (ELO 900) → ELO équipe = 900
- Probabilité de victoire pour A: P(A) = 0.71, pour B: P(B) = 1 - P(A) = 0.29
- Facteurs K: A1: K=50, A2: K=100, B1: K=100, B2: K=100
- A bat B 10-5
- Points gagnés par A1: +14 ELO (K=50 * (1-0.71))
- Points gagnés par A2: +29 ELO (K=100 * (1-0.71))
- Points perdus par B1: -29 ELO (K=100 * (0-0.29))
- Points perdus par B2: -29 ELO (K=100 * (0-0.29))

> *Cette logique de calcul sera implémentée dans le backend FastAPI, probablement déclenchée lors de l'enregistrement d'un nouveau match via un endpoint API.*

## Implémentation et développement

### Structure du projet

```markdown
baby_foot_elo/
├── frontend/               # Application Next.js
│   ├── pages/              # Routes de l'application
│   ├── components/         # Composants React réutilisables
│   ├── hooks/              # Hooks personnalisés
│   ├── styles/             # Styles CSS/Tailwind
│   ├── services/           # Fonctions pour appeler l'API backend
│   ├── utils/              # Utilitaires divers
│   └── public/             # Assets statiques
│
├── backend/                # Application FastAPI
│   ├── app/                # Code source de l'application
│   │   ├── main.py         # Point d'entrée FastAPI
│   │   ├── routers/        # Fichiers de routes (endpoints API)
│   │   ├── models/         # Modèles Pydantic (validation de données)
│   │   ├── schemas/        # Schémas de base de données (si ORM utilisé)
│   │   ├── crud/           # Fonctions d'accès aux données (CRUD)
│   │   ├── core/           # Configuration, logique métier centrale
│   │   └── db/             # Gestion de la connexion DuckDB
│   ├── tests/              # Tests unitaires/intégration
│   └── .env                # Variables d'environnement (ex: chemin DB)
│
├── data/                   # Données persistantes
│   └── babyfoot_elo.duckdb # Fichier de base de données DuckDB
│
└── docs/                   # Documentation
    ├── capture/            # Captures d'écran et maquettes
    └── project.md          # Ce document
```

### Interaction Frontend-Backend

L'interaction entre le frontend Next.js et le backend FastAPI se fera via des appels API RESTful:

- **Client HTTP dans Next.js:** Utilisation de `fetch` ou d'une librairie comme `axios` pour envoyer des requêtes aux endpoints définis dans FastAPI.
  - Exemple: `fetch('/api/v1/joueurs')` pour lister les joueurs.
  - Exemple: `POST /api/v1/matchs` avec les données du match pour enregistrer un résultat.
- **Endpoints FastAPI:** Le backend expose des endpoints pour chaque fonctionnalité (CRUD joueurs, équipes, matchs, calcul ELO, classements, etc.).
  - `/joueurs`, `/matchs`, `/equipes`, `/classements`, etc.
- **Authentification:** Une stratégie d'authentification devra être mise en place (ex: JWT tokens) si des fonctionnalités nécessitent une protection. FastAPI offre des outils pour cela.

### Considérations d'interface utilisateur

- Interface responsive pour utilisation sur mobile et desktop
- Système de thèmes clair/sombre avec préférence utilisateur sauvegardée
- Animations subtiles pour les mises à jour d'ELO
- Couleur dominante: vert islamique (#009432)
- Icônes et visuels en rapport avec le baby-foot
- Tableaux triables et filtrables
- Graphiques interactifs avec informations au survol

### Prérequis de développement

- **Frontend:**
  - Node.js v16+
  - npm (ou yarn/pnpm)
- **Backend:**
  - Python 3.8+
  - Poetry (pour la gestion des dépendances et de l'environnement virtuel)
  - FastAPI, Uvicorn (serveur ASGI), DuckDB Python package, et autres dépendances gérées via `pyproject.toml`.
- **Environnement de développement:**
  - VSCode avec extensions recommandées (ESLint, Prettier, Python, Pylance)
  - Outils de formatage/linting (Prettier pour JS/TS, Black/Flake8/Ruff pour Python)

### Déploiement

- **Développement local**:
  - Frontend: `npm run dev` (port 3000)
  - Backend: `uvicorn app.main:app --reload` (port 8000 par défaut)
- **Production**:
  - **Frontend (Next.js):** Déploiement sur Vercel, Netlify, ou autre hébergeur Node.js/statique.
  - **Backend (FastAPI):**
    - Déploiement sur des plateformes comme Docker (via conteneurisation), Heroku, Render, Fly.io, ou un serveur VPS.
    - Le fichier DuckDB (`babyfoot_elo.duckdb`) doit être accessible par l'instance backend déployée (ex: via un volume persistant si conteneurisé).
    - Utilisation d'un serveur ASGI plus robuste comme Gunicorn avec Uvicorn workers.
  - **Base de données (DuckDB):** Le fichier de base de données est géré avec l'application backend. Des stratégies de sauvegarde régulières du fichier `.duckdb` sont nécessaires.

### Considérations pour les classements périodiques

- Chaque match est automatiquement catégorisé par année et mois lors de son enregistrement via l'API.
- Le backend calcule et maintient les classements périodiques (potentiellement dans les tables dédiées `Classements_Periodiques` et `Classements_Equipes_Periodiques`).
- Les classements sont mis à jour après chaque match via la logique backend.
- Performance optimisée via l'indexation SQL des champs temporels et ID dans DuckDB.
- Possibilité d'ajouter des endpoints API pour recalculer l'historique complet si nécessaire.
