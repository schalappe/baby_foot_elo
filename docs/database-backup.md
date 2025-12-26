# Database Backup System

This document explains the automated backup system for the Baby Foot ELO Supabase database.

## Overview

The backup system creates daily snapshots of all database tables and stores them as JSON files in GitHub Artifacts. This provides protection against accidental data deletion and allows restoration to any backup point within 30 days.

## Architecture

```mermaid
flowchart LR
    A[GitHub Actions<br/>Daily 2 AM UTC] --> B[Fetch Tables via<br/>Supabase REST API]
    B --> C[Export as JSON Files]
    C --> D[Create .tar.gz Archive]
    D --> E[Store as Artifact<br/>30-day retention]
```

## What Gets Backed Up

All tables are backed up in the correct order to respect foreign key constraints:

1. `players` - Player profiles and ELO ratings
2. `teams` - Team compositions and team ELO
3. `matches` - Match results and metadata
4. `players_elo_history` - Player ELO change history
5. `teams_elo_history` - Team ELO change history

## Backup Schedule

- **Automated**: Every day at 2:00 AM UTC
- **Manual**: Can be triggered anytime via GitHub Actions
- **Retention**: 30 days (configurable in workflow)

## Setup Instructions

### 1. Add GitHub Secrets

GitHub Secrets store your Supabase credentials securely.

**Path**: Repository → Settings → Secrets and variables → Actions → Repository secrets

Add the following secrets:

| Secret Name    | Value                                      | Where to Find                                                            |
| -------------- | ------------------------------------------ | ------------------------------------------------------------------------ |
| `SUPABASE_URL` | `https://rdjdjscjgozpvbtjjzrf.supabase.co` | Supabase Dashboard → Project Settings → API                              |
| `SUPABASE_KEY` | Your publishable key (`sb_publishable_...`) | Supabase Dashboard → Project Settings → API → API Keys → Publishable key |

**Steps**:

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret listed above

### 2. Push the Backup Code

```bash
# Commit the backup system
git add scripts/ .github/workflows/ .gitignore docs/
git commit -m "feat: add automated database backup system"
git push
```

### 3. Verify the Workflow

After pushing:

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. Select **Database Backup** workflow
4. Click **Run workflow** → **Run workflow** (manual test)
5. Wait for completion (~1 minute)
6. Verify a backup artifact was created

## How to Access Backups

### Via GitHub UI

1. Go to your repository on GitHub
2. Navigate to **Actions** tab
3. Click on a **Database Backup** workflow run
4. Scroll to the bottom to the **Artifacts** section
5. Download the `database-backup-xxxxx.zip` file

```text
┌─────────────────────────────────────┐
│         Workflow Run Details        │
├─────────────────────────────────────┤
│ ...                                 │
│                                     │
│ Artifacts                           │
│ ──────────────────────────────────  │
│ database-backup-12345678    12 KB   │
│                          [Download] │
└─────────────────────────────────────┘
```

The downloaded file is a `.zip` containing your `.tar.gz` backup.

### Backup File Structure

When extracted, each backup contains:

```text
backup_20251226_020000/
├── players.json                 # All player records
├── teams.json                   # All team records
├── matches.json                 # All match records
├── players_elo_history.json     # Player ELO history
├── teams_elo_history.json       # Team ELO history
└── metadata.json                # Backup metadata
```

## Manual Backup (Local)

You can create backups locally using the provided script.

### Prerequisites

- `jq` installed (`brew install jq` on macOS)
- Your Supabase credentials

### Run Manual Backup

```bash
cd /Users/schalappe/Documents/Lab/Engineer/Projects/baby_foot_elo

# Set credentials (get these from .env)
export SUPABASE_URL="https://rdjdjscjgozpvbtjjzrf.supabase.co"
export SUPABASE_KEY="sb_publishable_..."  # Your publishable key

# Run backup
./scripts/backup_supabase.sh
```

**Output**:

```text
[INFO] Starting backup to ./backups/20251226_143022
[INFO] Backing up table: players
[INFO]   -> 15 records saved
[INFO] Backing up table: teams
[INFO]   -> 42 records saved
[INFO] Backing up table: matches
[INFO]   -> 128 records saved
[INFO] Backing up table: players_elo_history
[INFO]   -> 256 records saved
[INFO] Backing up table: teams_elo_history
[INFO]   -> 256 records saved
[INFO] Creating compressed archive...
[INFO] Backup complete: ./backups/backup_20251226_143022.tar.gz
[INFO] Cleaning old backups (keeping last 10)...
[INFO] Done!
```

Backups are saved to `./backups/backup_YYYYMMDD_HHMMSS.tar.gz`

## How to Restore from Backup

### Quick Reference

```bash
# 1. Install prerequisites
brew install libpq jq && brew link libpq --force

# 2. Get DATABASE_URL from Supabase Dashboard:
#    Settings → Database → Connection string → URI

# 3. Restore
export DATABASE_URL="postgresql://postgres:password@db.xxx.supabase.co:5432/postgres"
./scripts/restore_supabase.sh backups/backup_YYYYMMDD_HHMMSS.tar.gz
```

**Key Changes from Previous Version:**

- ✅ Now uses `DATABASE_URL` (not `SUPABASE_URL` + `SUPABASE_KEY`)
- ✅ Requires `psql` installed
- ✅ Automatically resets identity sequences
- ✅ Preserves original IDs (critical for data integrity)

---

### Prerequisites

**Required Tools:**

- `psql` (PostgreSQL client)
- `jq` (JSON processor)

**Install on macOS:**

```bash
brew install libpq jq
brew link libpq --force
```

**Why psql is needed**: The restore script uses direct PostgreSQL connection to insert data with `OVERRIDING SYSTEM VALUE`, which allows restoring original IDs for identity columns. The Supabase REST API doesn't support this operation.

### Step 1: Get Your Database Connection String

You need your direct PostgreSQL connection URL (not the REST API URL).

**Get it from Supabase Dashboard:**

1. Go to **Settings** → **Database**
2. Scroll to **Connection string** section
3. Select **URI** tab
4. Copy the full connection string (format: `postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres`)

**Example:**

```text
postgresql://postgres:your-password@db.rdjdjscjgozpvbtjjzrf.supabase.co:5432/postgres
```

### Step 2: Download Backup

- **From GitHub**: Download from Actions → Artifacts
- **Local**: Use existing backup from `./backups/`

Extract the `.zip` (if from GitHub) to get the `.tar.gz` file.

### Step 3: Run Restore Script

```bash
cd /Users/schalappe/Documents/Lab/Engineer/Projects/baby_foot_elo

# Set database connection string
export DATABASE_URL="postgresql://postgres:your-password@db.xxx.supabase.co:5432/postgres"

# Restore from backup
./scripts/restore_supabase.sh backups/backup_20251226_020000.tar.gz
```

**What happens:**

1. Script tests database connection
2. Extracts backup archive
3. Prompts for confirmation:
   ```text
   [WARN] This will INSERT data into your database.
   [WARN] Make sure the tables are empty or you may get duplicate key errors.
   Continue? (y/N)
   ```
4. Restores each table with original IDs
5. Automatically resets all identity sequences
6. Cleans up temporary files

**Expected Output:**

```text
[INFO] Testing database connection...
[INFO] Database connection successful.
[INFO] Extracting backup to /var/folders/.../tmp.xxxxx
[WARN] This will INSERT data into your database.
[WARN] Make sure the tables are empty or you may get duplicate key errors.
Continue? (y/N) y
[INFO] Restoring table players: 19 records...
[INFO]   -> Success
[INFO] Restoring table teams: 171 records...
[INFO]   -> Success
[INFO] Restoring table matches: 492 records...
[INFO]   -> Success
[INFO] Restoring table players_elo_history: 1000 records...
[INFO]   -> Success
[INFO] Restoring table teams_elo_history: 984 records...
[INFO]   -> Success
[INFO] Resetting identity sequences...
[INFO] Restore complete!
```

### Step 4: Verify Restoration

Check that your data was restored correctly:

1. Open your application
2. Check player rankings
3. Verify recent matches appear
4. Test creating a new player/match

## Restore Scenarios

### Scenario 1: Accidental Data Deletion

**Problem**: You accidentally deleted all players.

**Solution**:

1. Find the most recent backup before deletion
2. Download and restore it
3. Reset sequences
4. Verify data integrity

### Scenario 2: Database Corruption

**Problem**: Database is in an inconsistent state.

**Solution**:

1. Identify when the corruption occurred
2. Restore from a backup before that time
3. Reset sequences
4. Recreate any data added after the backup manually

### Scenario 3: Testing/Development

**Problem**: Need a copy of production data for testing.

**Solution**:

1. Download latest backup
2. Create a new Supabase project for testing
3. Restore backup to the test project
4. Update `.env` files to point to test database

## Backup Retention Policy

| Backup Type    | Retention     | Storage Location       |
| -------------- | ------------- | ---------------------- |
| GitHub Actions | 30 days       | GitHub Artifacts       |
| Local Manual   | Until deleted | `./backups/` directory |

**Notes**:

- GitHub automatically deletes artifacts after 30 days
- Local backups: Script keeps last 10, you can change this in the script
- Download important backups for long-term storage

## Troubleshooting

### Backup Fails with "401 Unauthorized"

**Cause**: GitHub secrets are incorrect or expired.

**Solution**:

1. Go to Supabase Dashboard → Project Settings → API → API Keys
2. Copy the publishable key (`sb_publishable_...`)
3. Update the `SUPABASE_KEY` secret in GitHub
4. Re-run the workflow

### Restore Fails: "psql is required but not installed"

**Cause**: PostgreSQL client tools are not installed.

**Solution**:

```bash
# macOS
brew install libpq
brew link libpq --force

# Ubuntu/Debian
sudo apt-get install postgresql-client

# Verify installation
psql --version
```

### Restore Fails: "Failed to connect to database"

**Cause**: Invalid `DATABASE_URL` or network connectivity issue.

**Solution**:

1. Verify your DATABASE_URL format:
   ```text
   postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
   ```
2. Get the correct URL from Supabase Dashboard → Settings → Database → Connection string → URI
3. Ensure your password doesn't contain special characters that need URL encoding
4. Test connection manually:
   ```bash
   psql "$DATABASE_URL" -c "SELECT 1"
   ```

### Restore Fails with "cannot insert a non-DEFAULT value into column"

**Cause**: This error should not occur with the updated script, but if it does, the `OVERRIDING SYSTEM VALUE` clause may not be working.

**Solution**:

1. Verify you're using the latest version of the restore script
2. Check that your PostgreSQL version supports `OVERRIDING SYSTEM VALUE` (9.6+)
3. Manually verify the generated SQL in `/tmp/` if the error persists

### Restore Fails with "Duplicate Key Error"

**Cause**: Data already exists in the target tables with the same IDs.

**Solution**:

1. Delete existing data from tables (in reverse dependency order):
   ```sql
   DELETE FROM teams_elo_history;
   DELETE FROM players_elo_history;
   DELETE FROM matches;
   DELETE FROM teams;
   DELETE FROM players;
   ```
2. Or truncate all tables (faster for large datasets):
   ```sql
   TRUNCATE teams_elo_history, players_elo_history, matches, teams, players CASCADE;
   ```
3. Re-run the restore script

### Backup Contains 0 Records

**Cause**: Tables were empty at backup time.

**Solution**:

- This is expected if the backup ran when the database was empty
- Use an earlier backup with actual data

### Restore Succeeds But New Records Get Wrong IDs

**Cause**: Identity sequences were not properly reset.

**Solution**:
The script should reset sequences automatically. If IDs are still wrong:

1. Manually reset sequences in Supabase SQL Editor:
   ```sql
   SELECT setval(pg_get_serial_sequence('players', 'player_id'), COALESCE(MAX(player_id), 1)) FROM players;
   SELECT setval(pg_get_serial_sequence('teams', 'team_id'), COALESCE(MAX(team_id), 1)) FROM teams;
   SELECT setval(pg_get_serial_sequence('matches', 'match_id'), COALESCE(MAX(match_id), 1)) FROM matches;
   SELECT setval(pg_get_serial_sequence('players_elo_history', 'history_id'), COALESCE(MAX(history_id), 1)) FROM players_elo_history;
   SELECT setval(pg_get_serial_sequence('teams_elo_history', 'history_id'), COALESCE(MAX(history_id), 1)) FROM teams_elo_history;
   ```
2. Verify sequences:
   ```sql
   SELECT last_value FROM players_player_id_seq;
   SELECT MAX(player_id) FROM players;
   ```

### Restore Hangs or Takes Too Long

**Cause**: Large dataset or slow network connection.

**Solution**:

1. The script runs all inserts in a single transaction per table, which can take time
2. Monitor progress - check Supabase Dashboard → Database → Table Editor
3. For very large restores (>10K records per table), consider breaking the backup into smaller chunks

## Security Considerations

### Secrets Management

**For Backups:**

- ✅ **DO**: Store credentials in GitHub Secrets
- ✅ **DO**: Use the publishable key (`sb_publishable_...`) for REST API access
- ❌ **DON'T**: Use the secret key (`sb_secret_...`) - it bypasses RLS
- ❌ **DON'T**: Commit credentials to the repository
- ❌ **DON'T**: Share backup files publicly (they contain your data)

**For Restores:**

- ✅ **DO**: Use `DATABASE_URL` from environment variables (never hardcode it)
- ✅ **DO**: Protect your database password - it grants full database access
- ⚠️ **CAUTION**: The `DATABASE_URL` contains your database password in plaintext
- ❌ **DON'T**: Share your `DATABASE_URL` or commit it to version control
- ❌ **DON'T**: Use the database connection string in production application code (use Supabase client instead)

### Backup Files

- Backups contain all your database data in plaintext JSON
- Download backups only to secure locations
- Delete local backups when no longer needed
- Don't commit `backups/` directory (already in `.gitignore`)

## Maintenance

### Updating Backup Tables

If you add new tables to your database, update the backup scripts:

**1. Edit `.github/workflows/backup-database.yml`**:

```yaml
TABLES=("players" "teams" "matches" "players_elo_history" "teams_elo_history" "new_table")
```

**2. Edit `scripts/backup_supabase.sh`**:

```bash
TABLES=("players" "teams" "matches" "players_elo_history" "teams_elo_history" "new_table")
```

**3. Edit `scripts/restore_supabase.sh`**:

```bash
TABLES=("players" "teams" "matches" "players_elo_history" "teams_elo_history" "new_table")
```

**Important**: Maintain table order to respect foreign key constraints!

### Changing Backup Schedule

Edit `.github/workflows/backup-database.yml`:

```yaml
on:
  schedule:
    # Run at 2 AM UTC daily
    - cron: "0 2 * * *"

    # Run every 6 hours
    # - cron: '0 */6 * * *'

    # Run weekly on Sundays
    # - cron: '0 0 * * 0'
```

Use [crontab.guru](https://crontab.guru/) to generate cron expressions.

### Extending Retention Period

Edit `.github/workflows/backup-database.yml`:

```yaml
- name: Upload backup artifact
  uses: actions/upload-artifact@v4
  with:
    name: database-backup-${{ github.run_id }}
    path: backups/*.tar.gz
    retention-days: 90 # Change from 30 to 90 days
```

**Note**: GitHub has storage limits - monitor your usage.

## Cost Analysis

| Component          | Cost                                     |
| ------------------ | ---------------------------------------- |
| GitHub Actions     | Free (2,000 min/month for private repos) |
| Artifact Storage   | Free (included in GitHub plan)           |
| Supabase API Calls | Free (within Supabase limits)            |
| **Total**          | **$0/month**                             |

**Usage estimates**:

- Each backup run: ~1 minute
- Daily backups: 30 runs/month
- Well within free tier limits

## Comparison with Supabase Pro Backups

| Feature           | GitHub Backup (This System)      | Supabase Pro PITR                   |
| ----------------- | -------------------------------- | ----------------------------------- |
| **Cost**          | Free                             | $25/month + $100/month (PITR addon) |
| **Frequency**     | Daily (customizable)             | Continuous (2-min intervals)        |
| **Retention**     | 30 days (customizable)           | 7-14 days                           |
| **Granularity**   | Daily snapshots                  | Point-in-time (any second)          |
| **Recovery Time** | ~5 minutes                       | ~15 minutes - hours                 |
| **Data Control**  | You own the files                | Supabase-managed                    |
| **Storage**       | GitHub (unlimited for artifacts) | Supabase servers                    |

**Recommendation**: Use both for maximum protection:

- Supabase PITR: Quick recovery for recent issues
- GitHub backups: Long-term archive and cost-effective fallback

## Technical Details

### Why Direct PostgreSQL Connection for Restore?

The restore script uses `psql` (direct PostgreSQL connection) instead of the Supabase REST API because:

| Feature              | REST API                      | Direct PostgreSQL (`psql`)            |
| -------------------- | ----------------------------- | ------------------------------------- |
| **Identity Columns** | ❌ Cannot insert explicit IDs | ✅ Supports `OVERRIDING SYSTEM VALUE` |
| **ID Preservation**  | ❌ IDs get regenerated        | ✅ Original IDs preserved             |
| **Foreign Keys**     | ⚠️ May break relationships    | ✅ Maintains all relationships        |
| **Sequence Reset**   | ⚠️ Manual step required       | ✅ Automatic in script                |
| **Authentication**   | Requires API key              | Requires database password            |
| **Use Case**         | Read-only operations          | Full database operations              |

**Why this matters**: When restoring data, preserving the original IDs is critical because:

- Match records reference specific player and team IDs
- ELO history records reference specific matches
- Breaking these relationships would corrupt your data

### Backup vs Restore Methods

| Operation   | Method            | Authentication     | Why?                                                    |
| ----------- | ----------------- | ------------------ | ------------------------------------------------------- |
| **Backup**  | Supabase REST API | Publishable key    | Read-only, no special privileges needed                 |
| **Restore** | Direct PostgreSQL | Database password  | Requires `OVERRIDING SYSTEM VALUE` for identity columns |

## Alternative Backup Methods

### 1. pg_dump (PostgreSQL Native)

If you have direct database access:

```bash
pg_dump "postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres" > backup.sql
```

**Pros**: Complete database dump including schema
**Cons**: Requires direct connection (not available on Free tier)

### 2. Supabase CLI

```bash
supabase db dump -f backup.sql
```

**Pros**: Official tool, easy to use
**Cons**: Requires local Supabase CLI setup

### 3. Third-Party Services

Services like **BackupNinja** or **SimpleBackups** offer automated PostgreSQL backups.

**Pros**: Professional-grade features
**Cons**: Additional cost ($10-30/month)

## Support

For issues with the backup system:

1. Check the **Troubleshooting** section above
2. Review GitHub Actions logs for error messages
3. Verify Supabase credentials are current
4. Test manual backup locally to isolate the issue

## Related Documentation

- [Supabase Database Documentation](https://supabase.com/docs/guides/database)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Project Architecture](./project.md)
