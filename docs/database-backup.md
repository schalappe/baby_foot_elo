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

| Secret Name | Value | Where to Find |
|-------------|-------|---------------|
| `SUPABASE_URL` | `https://rdjdjscjgozpvbtjjzrf.supabase.co` | Supabase Dashboard → Project Settings → API |
| `SUPABASE_KEY` | Your anon/public key | Supabase Dashboard → Project Settings → API → `anon` `public` key |

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
│         Workflow Run Details         │
├─────────────────────────────────────┤
│ ...                                  │
│                                      │
│ Artifacts                            │
│ ──────────────────────────────────  │
│ database-backup-12345678    12 KB   │
│                          [Download]  │
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

# Set credentials (get these from backend/.env)
export SUPABASE_URL="https://rdjdjscjgozpvbtjjzrf.supabase.co"
export SUPABASE_KEY="your-anon-key-here"

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

### Step 1: Download Backup

- **From GitHub**: Download from Actions → Artifacts
- **Local**: Use existing backup from `./backups/`

Extract the `.zip` (if from GitHub) to get the `.tar.gz` file.

### Step 2: Run Restore Script

```bash
cd /Users/schalappe/Documents/Lab/Engineer/Projects/baby_foot_elo

# Set credentials
export SUPABASE_URL="https://rdjdjscjgozpvbtjjzrf.supabase.co"
export SUPABASE_KEY="your-anon-key-here"

# Restore from backup
./scripts/restore_supabase.sh backups/backup_20251226_020000.tar.gz
```

**Important**: The script will prompt for confirmation before restoring:

```sql
[WARN] This will INSERT data into your database.
[WARN] Make sure the tables are empty or you may get duplicate key errors.
Continue? (y/N)
```

### Step 3: Reset Database Sequences

After restoring, you **must** reset the auto-increment sequences to prevent ID conflicts.

Go to Supabase Dashboard → SQL Editor and run:

```sql
-- Reset all sequence counters to match the maximum IDs
SELECT setval(
    pg_get_serial_sequence('players', 'player_id'),
    COALESCE(MAX(player_id), 1)
) FROM players;

SELECT setval(
    pg_get_serial_sequence('teams', 'team_id'),
    COALESCE(MAX(team_id), 1)
) FROM teams;

SELECT setval(
    pg_get_serial_sequence('matches', 'match_id'),
    COALESCE(MAX(match_id), 1)
) FROM matches;

SELECT setval(
    pg_get_serial_sequence('players_elo_history', 'history_id'),
    COALESCE(MAX(history_id), 1)
) FROM players_elo_history;

SELECT setval(
    pg_get_serial_sequence('teams_elo_history', 'history_id'),
    COALESCE(MAX(history_id), 1)
) FROM teams_elo_history;
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

| Backup Type | Retention | Storage Location |
|-------------|-----------|------------------|
| GitHub Actions | 30 days | GitHub Artifacts |
| Local Manual | Until deleted | `./backups/` directory |

**Notes**:
- GitHub automatically deletes artifacts after 30 days
- Local backups: Script keeps last 10, you can change this in the script
- Download important backups for long-term storage

## Troubleshooting

### Backup Fails with "401 Unauthorized"

**Cause**: GitHub secrets are incorrect or expired.

**Solution**:
1. Go to Supabase Dashboard → Project Settings → API
2. Copy the current `anon` `public` key
3. Update the `SUPABASE_KEY` secret in GitHub
4. Re-run the workflow

### Restore Fails with "Duplicate Key Error"

**Cause**: Data already exists in the target tables.

**Solution**:
1. Delete existing data from tables (in order):
   ```sql
   DELETE FROM teams_elo_history;
   DELETE FROM players_elo_history;
   DELETE FROM matches;
   DELETE FROM teams;
   DELETE FROM players;
   ```
2. Re-run the restore script

### Backup Contains 0 Records

**Cause**: Tables were empty at backup time.

**Solution**:
- This is expected if the backup ran when the database was empty
- Use an earlier backup with actual data

### Sequences Not Resetting

**Cause**: SQL syntax error or permissions issue.

**Solution**:
1. Ensure you're running the SQL in Supabase SQL Editor (not the API)
2. Check that each query runs individually
3. Verify the table names match exactly (case-sensitive)

## Security Considerations

### Secrets Management

- ✅ **DO**: Store credentials in GitHub Secrets
- ✅ **DO**: Use the `anon` public key (not service role)
- ❌ **DON'T**: Commit credentials to the repository
- ❌ **DON'T**: Share backup files publicly (they contain your data)

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
    - cron: '0 2 * * *'

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
    retention-days: 90  # Change from 30 to 90 days
```

**Note**: GitHub has storage limits - monitor your usage.

## Cost Analysis

| Component | Cost |
|-----------|------|
| GitHub Actions | Free (2,000 min/month for private repos) |
| Artifact Storage | Free (included in GitHub plan) |
| Supabase API Calls | Free (within Supabase limits) |
| **Total** | **$0/month** |

**Usage estimates**:
- Each backup run: ~1 minute
- Daily backups: 30 runs/month
- Well within free tier limits

## Comparison with Supabase Pro Backups

| Feature | GitHub Backup (This System) | Supabase Pro PITR |
|---------|----------------------------|-------------------|
| **Cost** | Free | $25/month + $100/month (PITR addon) |
| **Frequency** | Daily (customizable) | Continuous (2-min intervals) |
| **Retention** | 30 days (customizable) | 7-14 days |
| **Granularity** | Daily snapshots | Point-in-time (any second) |
| **Recovery Time** | ~5 minutes | ~15 minutes - hours |
| **Data Control** | You own the files | Supabase-managed |
| **Storage** | GitHub (unlimited for artifacts) | Supabase servers |

**Recommendation**: Use both for maximum protection:
- Supabase PITR: Quick recovery for recent issues
- GitHub backups: Long-term archive and cost-effective fallback

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
