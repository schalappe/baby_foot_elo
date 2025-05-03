# Baby Foot ELO

## Description

Le baby-foot, également connu sous le nom de football de table, est un jeu de société où deux équipes de deux joueurs manipulent des figurines fixées sur des barres pour frapper une petite balle et tenter de marquer des buts dans le camp adverse. Au baby-foot, le terme "fanny" désigne une situation où une équipe ou un joueur termine une partie avec un score de zéro ou négatif.

Baby Foot ELO est une application web qui permet à un groupe d'individu de suivre un championnat de baby foot. Elle permet de calculer l'ELO (hybride) de chaque joueur et de les classer. Elle permet également de suivre les matchs joués et les résultats.

## Fonctionnalités

- Enregistrement des joueurs
- Deduction automatique des pairs d'équipes
- Enregistrement des matchs (vainqueur, perdant, fanny)
- Calcul de l'ELO de chaque joueur
- Calculation de l'ELO de chaque équipe
- Classement des joueurs par ELO
- Classement des équipes par ELO
- Affichage des résultats des matchs et des ELO gagnés / perdus
- Export des résultats des matchs en JSON
- Affichage du classement des joueurs par ELO
- Affichage du classement des équipes par ELO

## Différentes pages

### Page d'accueil

![page d'accueil](./capture/home_page.png)
![template pade d'accueil](./capture/template_homepage.png)

- Affichage du classement des joueurs par ELO
- Affichage du classement des équipes par ELO

### Page d'information d'un joueur

![page d'information d'un joueur](./capture/template_player.png)

Une page par joueur

- Affichage des informations du juoeur
- Courbe de variation de l'ELO du joueur
- Affichage des résultats des matchs et des ELO gagnés / perdus
- Affichage du pourcentage de victoire avec les autres joueurs

### Page des résultats

![page des résultats](./capture/add_match.png)

- Enregistrement des matchs:
    - vainqueur / perdant
    - score de chaque équipe
- Affichage des résultats des matchs et des ELO gagnés / perdus
- Export des résultats des matchs en JSON

### Page de gestion des joueurs

![page de gestion des joueurs](./capture/add_player.png)

- Enregistrement des joueurs
- Deduction automatique des pairs d'équipes

## Technologies utilisées

- Front-end: Next.js
- Back-end: FastAPI
- Base de données: DuckDB
