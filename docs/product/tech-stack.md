# Tech Stack

## Overview

Baby Foot ELO uses a modern full-stack architecture with clear separation between frontend and backend, connected via REST API and backed by Supabase (PostgreSQL).

```text
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js 15)                  │
│              Port 3000 | App Router | TypeScript            │
├─────────────────────────────────────────────────────────────┤
│                         REST API                            │
├─────────────────────────────────────────────────────────────┤
│                     Backend (FastAPI)                       │
│              Port 8000 | Python 3.12+ | Pydantic            │
├─────────────────────────────────────────────────────────────┤
│                    Database (Supabase)                      │
│              PostgreSQL | RPC Functions | Auth              │
└─────────────────────────────────────────────────────────────┘
```

## Frontend

### Frontend Framework

| Technology | Version | Purpose                         |
| ---------- | ------- | ------------------------------- |
| Next.js    | 15      | React framework with App Router |
| React      | 19      | UI component library            |
| TypeScript | 5.x     | Type-safe JavaScript            |
| Turbopack  | -       | Fast development bundler        |

### UI & Styling

| Technology   | Purpose                         |
| ------------ | ------------------------------- |
| Tailwind CSS | Utility-first CSS framework     |
| ShadCN UI    | Accessible component primitives |
| Lucide Icons | Icon library                    |

### Data Fetching

| Technology | Purpose                                   |
| ---------- | ----------------------------------------- |
| SWR        | React hooks for data fetching and caching |
| Axios      | HTTP client for API requests              |

### Frontend Development Tools

| Tool     | Purpose                             |
| -------- | ----------------------------------- |
| Bun      | Fast JavaScript runtime and bundler |
| ESLint   | Code linting                        |
| Prettier | Code formatting                     |

## Backend

### Backend Framework

| Technology | Version | Purpose                           |
| ---------- | ------- | --------------------------------- |
| FastAPI    | 0.x     | Async Python web framework        |
| Python     | 3.12+   | Programming language              |
| Uvicorn    | -       | ASGI server                       |
| Pydantic   | 2.x     | Data validation and serialization |

### Architecture Pattern

```text
Endpoints (API Layer)
    ↓
Services (Business Logic)
    ↓
Repositories (Data Access)
    ↓
Supabase Client (Database)
```

### Backend Development Tools

| Tool   | Purpose                                |
| ------ | -------------------------------------- |
| Poetry | Dependency management                  |
| Black  | Code formatting (119 char line length) |
| isort  | Import sorting                         |
| Pylint | Code linting                           |

## Database

### Platform

| Technology | Purpose                           |
| ---------- | --------------------------------- |
| Supabase   | Managed PostgreSQL with API layer |
| PostgreSQL | Relational database               |

### Data Model

```text
Players (id, name, elo, created_at)
    ↓
Teams (id, player1_id, player2_id, elo, created_at)
    ↓
Matches (id, winner_team_id, loser_team_id, fanny, created_at)
    ↓
Player_History (id, player_id, match_id, elo_change, elo_after)
Team_History (id, team_id, match_id, elo_change, elo_after)
```

### SQL Functions (RPC)

| Function                   | Purpose                             |
| -------------------------- | ----------------------------------- |
| get_all_players_with_stats | Player rankings with computed stats |
| get_all_teams_with_stats   | Team rankings with computed stats   |
| get_player_full_stats      | Detailed player statistics          |
| get_player_matches_json    | Player match history (paginated)    |
| get_team_match_history     | Team match history                  |

## Infrastructure

### Development

| Component  | Configuration                       |
| ---------- | ----------------------------------- |
| Frontend   | `bun run dev` (localhost:3000)      |
| Backend    | `uvicorn --reload` (localhost:8000) |
| Concurrent | `bun run dev` from root runs both   |

### Deployment

| Platform | Component | Runtime     | Configuration                 |
| -------- | --------- | ----------- | ----------------------------- |
| Vercel   | Frontend  | Bun 1.x     | `vercel.json` with bunVersion |
| TBD      | Backend   | Python 3.12 | -                             |

**Vercel Configuration (`frontend/vercel.json`):**

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "bunVersion": "1.x"
}
```

This configuration ensures:

- Vercel uses Bun runtime instead of Node.js
- Automatic package manager detection via `bun.lock` file
- Consistent runtime between local development and production

### Environment Variables

**Backend (.env):**

- `FRONTEND_URL` — CORS allowed origin
- `SUPABASE_URL` — Supabase project URL
- `SUPABASE_KEY` — Supabase anonymous key

**Frontend (.env):**

- `NEXT_PUBLIC_API_URL` — Backend API base URL
- `NEXT_PUBLIC_SUPABASE_URL` — Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` — Supabase anonymous key

## Key Technical Decisions

### Why Hybrid ELO with Pool Correction?

Standard ELO in team games either:

1. Treats the team as a single entity (losing individual granularity)
2. Gives equal points to teammates (ignoring skill differences)

Our hybrid approach calculates individual changes based on personal K-factors while pool correction ensures the total ELO across all 4 players remains constant after each match.

### Why Supabase over Direct PostgreSQL?

- Managed infrastructure reduces ops burden
- Built-in RPC for complex SQL queries
- Row-level security ready for future auth
- Real-time subscriptions available for future features

### Why FastAPI + Next.js?

- Clear API contract between frontend and backend
- Python excels at mathematical calculations (ELO)
- Next.js provides excellent React DX with App Router
- Both support TypeScript/type hints for safety

### Why Bun over npm?

- **Speed**: Up to 30x faster than npm for install operations
- **All-in-one**: Runtime, bundler, package manager, and test runner in one tool
- **Drop-in replacement**: Uses the same `package.json` and npm registry
- **Better DX**: Faster feedback loops during development
- **Vercel support**: First-class support on Vercel deployment platform
