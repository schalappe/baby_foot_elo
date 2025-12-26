# Local Testing with Supabase

This guide explains how to run tests locally using a local Supabase instance instead of the production database.

## Overview

The test suite is configured to use a local Supabase instance for isolation and faster test execution. This separates test data from production and allows parallel development without affecting the live database.

## Prerequisites

- **Supabase CLI**: Install with `brew install supabase/tap/supabase` (macOS) or see [Supabase CLI docs](https://supabase.com/docs/guides/cli)
- **Docker**: Required for local Supabase (install from [Docker Desktop](https://www.docker.com/products/docker-desktop))

## Quick Start

### 1. Start Local Supabase

```bash
bun run supabase:start
```

This command:
- Starts PostgreSQL, PostgREST, Auth, Realtime, and Studio in Docker containers
- Applies migrations from `supabase/migrations/`
- Makes services available on localhost ports (default: 54321 for API)

### 2. Run Tests

```bash
bun run test
```

Tests automatically use `.env.test` which points to the local Supabase instance.

### 3. Stop Local Supabase

```bash
bun run supabase:stop
```

## Environment Configuration

### `.env` (Development)

Used by `make dev` for the Next.js development server:
```env
NEXT_PUBLIC_SUPABASE_URL="https://your-project.supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="your-production-anon-key"
```

### `.env.test` (Testing)

Used by `vitest` for running tests:
```env
NEXT_PUBLIC_SUPABASE_URL="http://127.0.0.1:54321"
NEXT_PUBLIC_SUPABASE_ANON_KEY="eyJhbGc..."  # Local Supabase default anon key
```

**Note**: `.env.test` is ignored by git. The default local anon key is safe to commit as it only works for local development.

## Available Scripts

| Command | Description |
|---------|-------------|
| `bun run test` | Run tests using local Supabase (must be started first) |
| `bun run test:run` | Same as `test` (runs once and exits) |
| `bun run test:local` | Start Supabase, reset DB with migrations, run tests, stop (portable) |
| `bun run supabase:start` | Start local Supabase containers |
| `bun run supabase:stop` | Stop local Supabase containers |
| `bun run supabase:status` | Check status of local Supabase services |
| `bun run supabase:reset` | Reset database to initial migration state |

## Workflow

### Standard Development

```bash
# Terminal 1: Start local Supabase (leave running)
bun run supabase:start

# Terminal 2: Run tests in watch mode
bun run test

# When done, stop Supabase
bun run supabase:stop
```

### CI/Automated Testing or Fresh Machine

```bash
# All-in-one command (starts, resets DB with migrations, tests, stops)
bun run test:local
```

This command is portable and works on any machine with Docker and Supabase CLI installed. It:
1. Starts local Supabase containers
2. Resets the database and applies all migrations from `supabase/migrations/`
3. Runs the test suite
4. Stops Supabase containers

## Local Supabase Ports

When running `supabase start`, services are available on:

| Service | Port | Description |
|---------|------|-------------|
| API (Kong) | 54321 | Main API gateway (PostgREST) |
| Database | 54322 | Direct PostgreSQL access |
| Studio | 54323 | Supabase Studio UI (http://localhost:54323) |
| Inbucket | 54324 | Email testing |
| Auth | 54325 | Auth service |
| Realtime | 54326 | Realtime subscriptions |

**Studio UI**: Access the local Supabase dashboard at http://localhost:54323 to inspect data, run queries, and manage the schema.

## Database Migrations

### Applying Migrations

Migrations in `supabase/migrations/` are automatically applied when you run `supabase start`. To manually reset the database:

```bash
bun run supabase:reset
```

This drops all tables and re-applies migrations from scratch.

### Creating Migrations

```bash
supabase migration new migration_name
```

Edit the generated file in `supabase/migrations/`, then reset to apply:

```bash
bun run supabase:reset
```

## Troubleshooting

### "Connection refused" errors

**Problem**: Tests fail with connection errors.

**Solution**: Ensure local Supabase is running:
```bash
bun run supabase:status
```

If not running:
```bash
bun run supabase:start
```

### Port conflicts

**Problem**: `supabase start` fails with "port already in use".

**Solution**: Stop conflicting services or change ports in `supabase/config.toml`.

### Stale data between test runs

**Problem**: Tests interfere with each other due to leftover data.

**Solution**: Reset the database:
```bash
bun run supabase:reset
```

### Tests passing locally but failing in CI

**Problem**: Tests use production Supabase in CI instead of local.

**Solution**: Ensure `.env.test` exists and CI uses `bun run test:local` which manages the Supabase lifecycle.

## Best Practices

1. **Start Supabase once**: Keep it running in a terminal while developing. No need to restart between test runs.
2. **Use watch mode**: Run `bun run test` to automatically re-run tests on code changes.
3. **Reset when needed**: If tests become flaky, run `bun run supabase:reset` to start fresh.
4. **Inspect with Studio**: Use http://localhost:54323 to debug test data and schema issues.
5. **Don't commit .env.test**: Keep local Supabase credentials out of version control (already in `.gitignore`).

## Architecture Notes

- **vitest.config.ts**: Automatically loads `.env.test` when running tests
- **Integration tests**: Located in `tests/integration/`, these test database operations
- **Unit tests**: Located in `tests/unit/`, these test pure logic without Supabase
- **Sequential execution**: Tests run one at a time to avoid database conflicts (configured in vitest.config.ts)

## Additional Resources

- [Supabase CLI Documentation](https://supabase.com/docs/guides/cli)
- [Local Development Guide](https://supabase.com/docs/guides/cli/local-development)
- [Vitest Documentation](https://vitest.dev/)
