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

### Backend & Base de Données (BaaS)

- Plateforme: **Supabase**
  - Solution Backend-as-a-Service (BaaS) basée sur PostgreSQL.
  - Fournit une base de données PostgreSQL managée.
  - Génère automatiquement une API REST et GraphQL.
  - Intègre l'authentification (Supabase Auth).
  - Permet l'exécution de logique backend via Edge Functions (Deno runtime).
  - Offre du stockage de fichiers (Supabase Storage).
  - Capacités temps réel (Supabase Realtime).

- Key information:
  - [Projet URL](https://kuahfdqrotzlyhebtizq.supabase.co)
  - Anon: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt1YWhmZHFyb3R6bHloZWJ0aXpxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYzNTMxOTgsImV4cCI6MjA2MTkyOTE5OH0.fTfX1Bd-SwYchfZAanrmmRCcIqqt1M_DggnQDDs_Bik

### Modèle de données

- **Joueurs**: `id`, `nom`, `avatar`, `elo`, `date_creation`
- **Équipes**: `id`, `joueur1_id` (FK to Joueurs), `joueur2_id` (FK to Joueurs), `dernier_match` *(Note: Represents a unique pair of players who have played together. Team ELO is calculated dynamically.)*
- **Matchs**: `id`, `équipe_gagnante_id` (FK to Équipes), `équipe_perdante_id` (FK to Équipes), `score_gagnant`, `score_perdant`, `est_fanny`, `date`, `année`, `mois`
- **Historique_ELO**: `id`, `joueur_id` (FK to Joueurs), `match_id` (FK to Matchs), `ancien_elo`, `nouvel_elo`, `difference`, `date`, `année`, `mois`
- **Classements_Périodiques**: `id`, `joueur_id` (FK to Joueurs), `année`, `mois`, `elo`, `position`, `matchs_joues`, `victoires`, `défaites` *(Note: Stores periodic PLAYER rankings.)*
- **Classements_Equipes_Periodiques**: `id`, `equipe_id` (FK to Équipes), `année`, `mois`, `elo_moyen`, `position`, `matchs_joues`, `victoires`, `défaites` *(Note: Stores periodic TEAM rankings.)*

*(Note: Le modèle est défini pour PostgreSQL via Supabase. Les types de données comme `DATETIME` correspondent à `TIMESTAMP WITH TIME ZONE` dans PostgreSQL.)*

#### Diagramme Entité-Relation

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
        INT id PK
        VARCHAR nom
        VARCHAR avatar
        INT elo
        DATETIME date_creation
    }

    EQUIPES {
        INT id PK
        INT joueur1_id FK
        INT joueur2_id FK
        DATETIME dernier_match
    }

    MATCHS {
        INT id PK
        INT equipe_gagnante_id FK
        INT equipe_perdante_id FK
        INT score_gagnant
        INT score_perdant
        BOOLEAN est_fanny
        DATETIME date
        INT annee
        INT mois
    }

    HISTORIQUE_ELO {
        INT id PK
        INT joueur_id FK
        INT match_id FK
        INT ancien_elo
        INT nouvel_elo
        INT difference
        DATETIME date
        INT annee
        INT mois
    }

    CLASSEMENTS_PERIODIQUES {
        INT id PK
        INT joueur_id FK
        INT annee
        INT mois
        INT elo
        INT position
        INT matchs_joues
        INT victoires
        INT defaites
    }

    CLASSEMENTS_EQUIPES_PERIODIQUES {
        INT id PK
        INT equipe_id FK
        INT annee
        INT mois
        FLOAT elo_moyen 
        INT position
        INT matchs_joues
        INT victoires
        INT defaites
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
  - Avatar et nom du joueur
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
  - Avatar et nom
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
  - Calcul en temps réel des points ELO potentiels
  - Date du match (défaut: actuelle)
- Historique complet des matchs
  - Filtrable par joueur, équipe ou période (année, mois)
  - Tri par date, importance du match (points ELO échangés)
  - Détails complets accessibles
- Bouton d'export en JSON
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
  - Upload d'avatar (optionnel)
  - ELO initial (modifiable, défaut 1000)
- Liste des joueurs existants
  - Fonctionnalités de recherche et tri
  - Option de modification/désactivation
  - Statistiques résumées
- Outil de génération d'équipes
  - Suggestion d'équipes équilibrées
  - Basé sur l'ELO ou d'autres critères
  - Utile pour organiser des matchs équitables
- Interface d'administration
  - Ajustements manuels d'ELO (avec journalisation)
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

> *Cette logique de calcul sera implémentée via des Supabase Edge Functions pour s'exécuter côté serveur.*

## Implémentation et développement

### Structure du projet

```markdown
baby_foot_elo/
├── frontend/               # Application Next.js
│   ├── pages/              # Routes de l'application
│   ├── components/         # Composants React réutilisables
│   ├── hooks/              # Hooks personnalisés
│   ├── styles/             # Styles CSS/Tailwind
│   ├── utils/              # Utilitaires (incluant client Supabase)
│   └── public/             # Assets statiques
│
├── supabase/               # Configuration et fonctions Supabase
│   ├── functions/          # Edge Functions (ex: calcul ELO)
│   │   └── ...
│   ├── migrations/         # Migrations de base de données SQL
│   │   └── ...
│   └── config.toml         # Configuration Supabase CLI
│
└── docs/                   # Documentation
    ├── capture/            # Captures d'écran et maquettes
    └── project.md          # Ce document
```

### Interaction avec Supabase (remplace les endpoints API dédiés)

L'interaction avec la base de données et les fonctionnalités backend se fera principalement via :

- **Client `supabase-js` dans Next.js:** Pour les opérations CRUD de base sur les tables (joueurs, équipes, matchs), l'authentification et l'écoute des changements en temps réel.
  - Exemple: `supabase.from('joueurs').select('*')` pour lister les joueurs.
  - Exemple: `supabase.auth.signUp({...})` pour l'inscription.
- **Supabase Edge Functions:** Pour la logique métier complexe qui doit s'exécuter côté serveur de manière sécurisée et performante.
  - **Calcul ELO Hybride:** Une fonction déclenchée après l'insertion d'un match pour calculer et mettre à jour les ELO des joueurs et les classements périodiques.
  - **Génération de classements:** Fonctions pour calculer les classements (joueurs, équipes) pour des périodes spécifiques si nécessaire (bien que les tables `Classements_Periodiques` visent à stocker ces snapshots).
  - **Export de données:** Une fonction pour générer l'export JSON.
- **Politiques RLS (Row Level Security) de PostgreSQL:** Pour définir des règles d'accès fines aux données directement dans la base de données.

### Considérations d'interface utilisateur

- Interface responsive pour utilisation sur mobile et desktop
- Système de thèmes clair/sombre avec préférence utilisateur sauvegardée
- Animations subtiles pour les mises à jour d'ELO
- Couleur dominante: vert islamique (#009432)
- Icônes et visuels en rapport avec le baby-foot
- Tableaux triables et filtrables
- Graphiques interactifs avec informations au survol

### Prérequis de développement

- Node.js v16+ pour le frontend (Next.js)
- npm (ou yarn/pnpm) pour la gestion des dépendances frontend
- Supabase CLI pour la gestion locale de l'environnement Supabase (migrations, fonctions)
- Deno (pour le développement et test local des Edge Functions)
- Environnement de développement:
  - VSCode avec extensions recommandées (ESLint, Prettier, Deno)
  - ESLint/Prettier pour le frontend et les fonctions Edge (TypeScript/JavaScript)

### Déploiement

- **Développement local**:
  - Frontend: `npm run dev` (port 3000)
  - Supabase local: `supabase start` (via Supabase CLI) pour émuler l'environnement Supabase (DB, Auth, Functions, Storage).
- **Production**:
  - **Frontend (Next.js):** Déploiement sur des plateformes comme Vercel, Netlify, ou autre hébergeur Node.js.
  - **Backend (Supabase):** Utilisation du projet Supabase Cloud managé. Les Edge Functions sont déployées via `supabase functions deploy`.
  - La base de données PostgreSQL est gérée par Supabase Cloud, incluant les sauvegardes.

### Considérations pour les classements périodiques

- Chaque match est automatiquement catégorisé par année et mois
- Le système calcule et maintient des classements distincts pour chaque période
- Les classements périodiques sont recalculés après chaque match
- Performance optimisée via l'indexation des champs temporels
- Possibilité de recalculer l'historique complet si nécessaire
