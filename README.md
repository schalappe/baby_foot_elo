# Baby Foot ELO

A web application for tracking foosball championships with a hybrid ELO rating system. Players form teams of two, and individual ELO changes are calculated based on each player's rating and team performance.

## Quick Start

```bash
# Install
git clone <repository-url>
cd baby_foot_elo
bun install

# Configure (get credentials from Supabase Dashboard → Project Settings → API)
cp .env.example .env
# Edit .env: add NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY

# Run
bun run dev
# Open http://localhost:3000
```

## Features

- **Hybrid ELO System**: Individual player and team ratings tracked independently
- **Zero-Sum Pool Correction**: Fair ELO economy with no rating inflation
- **K-Factor Tiers**: Fast progression for beginners (K=200), stable ratings for experts (K=50)
- **Real-Time Rankings**: Live leaderboards for players and teams
- **Match History**: ELO changes tracked per match for all participants

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind, ShadCN UI |
| Backend | Next.js API Routes, Supabase (PostgreSQL) |
| Infrastructure | Vercel, GitHub Actions (daily backups) |

## Development

```bash
bun run dev          # Start dev server
bun run build        # Production build
bun run test:local   # Run tests with local Supabase
bun run lint         # ESLint
bun run typecheck    # TypeScript check
```

### Local Testing

```bash
bun run supabase:start   # Start local Supabase (requires Docker)
bun run test             # Run tests
bun run supabase:stop    # Stop when done
```

## Project Structure

```text
app/                    # Next.js pages + API routes (/api/v1/)
components/             # React components
lib/
├── services/           # Business logic (ELO, matches, players)
├── db/repositories/    # Data access layer
└── api/client/         # Frontend API client
docs/                   # Comprehensive documentation
```

## API

```bash
# Players
GET  /api/v1/players/rankings
POST /api/v1/players

# Teams
GET  /api/v1/teams/rankings
POST /api/v1/teams

# Matches
GET  /api/v1/matches
POST /api/v1/matches
```

**Example**: Record a match
```bash
curl -X POST http://localhost:3000/api/v1/matches \
  -H "Content-Type: application/json" \
  -d '{"winner_team_id": 5, "loser_team_id": 3, "is_fanny": false}'
```

## Documentation

Detailed documentation available in `docs/`:

- **[Documentation Hub](./docs/README.md)** - Main navigation
- **[Technical Docs](./docs/technical/README.md)** - Architecture, database schema, ELO algorithm
- **[Operations](./docs/operations/README.md)** - Backup system, local testing
- **[Product](./docs/product/README.md)** - Mission, roadmap

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 3000 in use | `lsof -ti:3000 \| xargs kill -9` |
| DB connection fails | Check `.env` credentials |
| Tests fail | Run `bun run supabase:start` first |

## License

MIT
