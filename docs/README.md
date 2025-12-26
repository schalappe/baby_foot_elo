# Documentation Hub

Welcome to the Baby Foot ELO documentation. This hub provides organized access to all project documentation categorized by audience and purpose.

## 📁 Documentation Structure

```text
docs/
│
├── README.md (you are here)           # Main navigation hub
│
├── product/                           # Product documentation
│   ├── README.md                      # Product docs index
│   ├── mission.md                     # Product vision & personas
│   ├── roadmap.md                     # Feature roadmap
│   └── tech-stack.md                  # Technology choices
│
├── technical/                         # Technical documentation
│   ├── README.md                      # Technical docs index
│   ├── 01-architecture-overview.md    # System architecture (521 lines)
│   ├── 02-database-schema.md          # Database design (575 lines)
│   ├── 03-sequence-diagrams.md        # Flow diagrams (644 lines)
│   └── 04-elo-calculation-system.md   # ELO algorithm (682 lines)
│
└── operations/                        # Operations documentation
    ├── README.md                      # Operations docs index
    ├── database-backup.md             # Backup system & restoration
    └── local-testing.md               # Local testing with Supabase
```

---

## 📚 Quick Navigation

### For New Users
- [Product Mission](./product/mission.md) - What Baby Foot ELO is and why it exists
- [Getting Started](../README.md#quick-start) - Setup and run the application

### For Developers
- **New to the project?** → [Developer Onboarding](#developer-onboarding)
- **Working on features?** → [Technical Documentation](./technical/README.md)
- **Need API reference?** → [API Quick Reference](#api-quick-reference)

### For Operations
- [Database Backup System](./operations/database-backup.md) - Automated backups and restoration
- [Local Testing Guide](./operations/local-testing.md) - Testing with local Supabase

### For Product Managers
- [Product Documentation](./product/README.md) - Mission, roadmap, and tech stack

---

## 🚀 Developer Onboarding

### First-Time Setup (5 minutes)

1. **Clone and Install**
   ```bash
   git clone <repository-url>
   cd baby_foot_elo
   bun install
   ```

2. **Configure Environment**
   ```bash
   # Copy example env file
   cp .env.example .env

   # Get credentials from Supabase Dashboard
   # Add NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY
   ```

3. **Start Development**
   ```bash
   bun run dev
   # Open http://localhost:3000
   ```

### Understanding the Codebase (60 minutes)

**Recommended reading order:**

1. **[Architecture Overview](./technical/01-architecture-overview.md)** (20 min)
   - Understand the 6-layer architecture
   - Learn design patterns (Service, Repository, Mapper)
   - See technology stack

2. **[Class Diagrams](./technical/07-class-diagrams.md)** (15 min)
   - Visual system architecture with all layers
   - Component hierarchy and data flow
   - 13 comprehensive Mermaid diagrams

3. **[Database Schema](./technical/02-database-schema.md)** (10 min)
   - Review 5 core tables (players, teams, matches, history)
   - Understand relationships and constraints
   - See RPC function optimization

4. **[Sequence Diagrams](./technical/03-sequence-diagrams.md)** (10 min)
   - Focus on "Match Creation Flow" (9-step process)
   - See how components interact

5. **Deep Dive - Service & Repository Layers** (15 min)
   - **[Service Layer Reference](./technical/05-service-layer.md)** - Complete class documentation
     - All service functions with signatures, parameters, examples
     - ELO Service: Pure calculation functions
     - Match Service: 9-step match creation orchestration
     - Player/Team Services: Lifecycle management

   - **[Repository Layer Reference](./technical/06-repository-layer.md)** - Complete class documentation
     - All repository functions with CRUD operations
     - Retry patterns and batch operations
     - RPC-based statistics aggregation

6. **Optional: [ELO Calculation](./technical/04-elo-calculation-system.md)** (only if working on ELO logic)

### Code Exploration Guide

```bash
# Frontend (React/Next.js)
app/                    # Next.js pages (App Router)
components/             # React components (UI + feature)

# Backend (Next.js API Routes)
app/api/v1/            # REST API endpoints

# Business Logic
lib/services/          # Core business logic (ELO, matches, players, teams)
lib/db/repositories/   # Data access layer

# Database
supabase/              # SQL functions (RPC)
```

### Development Workflow

**Working on a feature:**

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Start dev server
bun run dev

# 3. Make changes, test in browser

# 4. Run tests
bun run test:local

# 5. Lint and format
bun run lint
bun run format

# 6. Commit
git add .
git commit -m "feat: add my feature"

# 7. Push and create PR
git push origin feature/my-feature
```

---

## 📡 API Quick Reference

### Base URL
- **Development**: `http://localhost:3000/api/v1`
- **Production**: `https://your-domain.vercel.app/api/v1`

### Core Endpoints

#### Players
```bash
GET    /players/rankings      # Get ranked player list
POST   /players               # Create new player
GET    /players/{id}          # Get player details
GET    /players/{id}/statistics  # Get player stats with ELO history
GET    /players/{id}/matches  # Get player's match history
```

#### Teams
```bash
GET    /teams/rankings        # Get ranked team list
POST   /teams                 # Create new team
GET    /teams/{id}            # Get team details
GET    /teams/{id}/statistics # Get team stats
```

#### Matches
```bash
GET    /matches               # Get matches (with filters)
POST   /matches               # Record new match
GET    /matches/{id}          # Get match details
DELETE /matches/{id}          # Delete match
GET    /matches/export        # Export matches (CSV/JSON)
```

### Example: Record a Match

```bash
curl -X POST http://localhost:3000/api/v1/matches \
  -H "Content-Type: application/json" \
  -d '{
    "winner_team_id": 5,
    "loser_team_id": 3,
    "is_fanny": false,
    "played_at": "2025-12-26T19:30:00Z",
    "notes": "Championship final"
  }'
```

**Response**:
```json
{
  "match_id": 42,
  "winner_team_id": 5,
  "loser_team_id": 3,
  "elo_changes": {
    "1": { "old_elo": 1600, "new_elo": 1624, "difference": 24 },
    "2": { "old_elo": 1400, "new_elo": 1424, "difference": 24 },
    "3": { "old_elo": 1200, "new_elo": 1184, "difference": -16 },
    "4": { "old_elo": 1100, "new_elo": 1067, "difference": -33 }
  }
}
```

---

## 🧪 Testing Guide

### Run All Tests
```bash
# Start local Supabase, reset DB, run tests, stop
bun run test:local
```

### Run Tests in Watch Mode
```bash
# Terminal 1: Start local Supabase (leave running)
bun run supabase:start

# Terminal 2: Run tests in watch mode
bun run test
```

### Test Structure
```text
tests/
├── unit/           # Pure logic tests (ELO calculations, utils)
└── integration/    # Database tests (repositories, services)
```

[→ Local Testing Guide](./operations/local-testing.md)

---

## 🛠 Common Tasks

### Adding a New Feature

1. **Plan** (if complex)
   - Read [Architecture Overview](./technical/01-architecture-overview.md)
   - Identify which layers need changes (Frontend, API, Service, Repository, Database)

2. **Database Changes** (if needed)
   ```bash
   # Create migration
   supabase migration new add_feature_table

   # Edit migration file
   # Apply migration
   bun run supabase:reset
   ```

3. **Backend Implementation**
   - Add repository functions (`lib/db/repositories/`)
   - Add service logic (`lib/services/`)
   - Create API route (`app/api/v1/`)
   - Add types (`types/`)

4. **Frontend Implementation**
   - Add components (`components/`)
   - Create page (`app/`)
   - Add API client call (`lib/api/client/`)

5. **Test**
   ```bash
   bun run test:local
   bun run dev  # Manual testing
   ```

### Modifying ELO Calculation

**⚠️ CRITICAL** - Changes must maintain:
- Zero-sum property (pool correction)
- K-factor tiers (200/100/50)
- Mathematical equivalence with Python implementation

[→ ELO Calculation System](./technical/04-elo-calculation-system.md)

### Database Schema Changes

1. Create migration:
   ```bash
   supabase migration new migration_description
   ```

2. Edit `supabase/migrations/XXXXXX_migration_description.sql`

3. Apply locally:
   ```bash
   bun run supabase:reset
   ```

4. Test thoroughly, then push migration to production

[→ Database Schema Guide](./technical/02-database-schema.md)

---

## 🔍 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Port 3000 already in use** | `lsof -ti:3000 \| xargs kill -9` |
| **Database connection fails** | Check `.env` has correct `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` |
| **Tests fail with connection error** | Run `bun run supabase:start` before tests |
| **ELO calculation seems wrong** | Verify pool correction is working (sum of changes ≈ 0) |
| **Backup fails in GitHub Actions** | Check GitHub Secrets (`SUPABASE_URL`, `SUPABASE_KEY`) |

### Getting Help

1. Check relevant documentation section above
2. Search issues in GitHub repository
3. Review error logs in terminal
4. Check Supabase Dashboard for database issues

---

## 📚 External Resources

### Technology Documentation
- [Next.js 16 Documentation](https://nextjs.org/docs)
- [React 19 Documentation](https://react.dev/)
- [Supabase Documentation](https://supabase.com/docs)
- [SWR Documentation](https://swr.vercel.app/)
- [TanStack Table](https://tanstack.com/table/latest)
- [ShadCN UI](https://ui.shadcn.com/)

### Related Concepts
- [ELO Rating System (Wikipedia)](https://en.wikipedia.org/wiki/Elo_rating_system)
- [K-Factor in ELO](https://en.wikipedia.org/wiki/Elo_rating_system#Most_accurate_K-factor)
- [Next.js App Router](https://nextjs.org/docs/app)
- [PostgreSQL RPC Functions](https://www.postgresql.org/docs/current/sql-createfunction.html)

---

**Last Updated**: 2025-12-26
**Maintained By**: Development Team
**Documentation Version**: 1.0
