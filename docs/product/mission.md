# Product Mission

## Pitch

Baby Foot ELO is a web application that helps foosball enthusiasts in offices and clubs track their competitive performance by providing a fair, transparent ELO-based ranking system that accounts for individual skill within team play.

## Users

### Primary Customers

- **Office Teams**: Companies with foosball tables who want to add friendly competition and track performance over time
- **Foosball Clubs**: Recreational clubs organizing regular tournaments and leagues

### User Personas

**The Casual Competitor** (25-40)

- **Role:** Office worker who plays foosball during breaks
- **Context:** Wants to know how they stack up against colleagues without manual spreadsheet tracking
- **Pain Points:** No easy way to track wins/losses, unclear who the "best" players actually are
- **Goals:** See personal improvement over time, have fun with competitive rankings

**The League Organizer** (30-50)

- **Role:** Person who organizes foosball events at work or club
- **Context:** Needs to track results for multiple players and teams fairly
- **Pain Points:** Manual tracking is tedious, basic win/loss doesn't account for opponent strength
- **Goals:** Fair rankings that motivate participation, historical data for tournaments

## The Problem

### No Fair Way to Track Foosball Performance

Traditional win/loss tracking doesn't account for opponent strength. Beating a beginner and beating a champion count the same. This demotivates skilled players and provides no clear progression path for newcomers.

**Our Solution:** A hybrid ELO system that tracks both individual and team ratings, ensuring players earn points proportional to the difficulty of their victories.

### Team Games, Individual Skills

In 2v2 foosball, teammates may have vastly different skill levels. Standard team-only ratings hide individual contribution and growth.

**Our Solution:** Individual ELO ratings that adjust based on personal K-factors, even when playing as a team. The pool correction system ensures zero-sum ELO across all participants.

## Differentiators

### Hybrid ELO System

Unlike simple win/loss trackers, we calculate individual ELO changes based on each player's rating and K-factor, even in team matches. This means two players on the same winning team may gain different points based on their experience level.

### Pool Correction for Fairness

Our system ensures total ELO remains constant across all players. No artificial inflation or deflation of ratings over time.

### K-Factor Tiers for Progression

- New players (ELO < 1200) use K=200 for rapid progression
- Intermediate players (1200-1800) use K=100 for balanced adjustment
- Experienced players (ELO >= 1800) use K=50 for stable rankings

This creates a natural progression curve where newcomers can climb quickly while established rankings remain stable.

## Key Features

### Core Features

- **Player Registration:** Add players with automatic ELO initialization at 1500
- **Team Formation:** Create 2-player teams with combined team ELO tracking
- **Match Recording:** Log match results with winner/loser designation and optional "fanny" flag for shutouts

### Statistics Features

- **Individual Rankings:** Leaderboard sorted by personal ELO with win/loss records
- **Team Rankings:** Team-based leaderboard with combined statistics
- **Match History:** Detailed history with ELO changes per match for players and teams
- **Player Profiles:** Individual statistics pages with performance trends

### Technical Features

- **Real-time Updates:** SWR-based data fetching with automatic cache invalidation
- **Responsive Design:** Works on desktop and mobile devices
- **API Documentation:** Full Swagger/ReDoc API documentation for integrations
