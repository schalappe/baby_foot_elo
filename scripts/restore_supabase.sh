#!/bin/bash
# Supabase Data Restore Script
# Restores data from a backup archive

set -e

# Configuration
SUPABASE_URL="${SUPABASE_URL:-}"
SUPABASE_KEY="${SUPABASE_KEY:-}"

# Tables in order for restoration (respects foreign key constraints)
TABLES=("players" "teams" "matches" "players_elo_history" "teams_elo_history")

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Validate arguments
if [ -z "$1" ]; then
    log_error "Usage: SUPABASE_URL=xxx SUPABASE_KEY=xxx ./restore_supabase.sh <backup_file.tar.gz>"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    log_error "Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

# Validate environment variables
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    log_error "SUPABASE_URL and SUPABASE_KEY environment variables are required"
    exit 1
fi

# Extract backup
TEMP_DIR=$(mktemp -d)
log_info "Extracting backup to ${TEMP_DIR}"
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# Find the extracted directory
BACKUP_DIR=$(find "$TEMP_DIR" -mindepth 1 -maxdepth 1 -type d | head -1)

if [ -z "$BACKUP_DIR" ]; then
    log_error "Could not find backup data in archive"
    rm -rf "$TEMP_DIR"
    exit 1
fi

log_warn "This will INSERT data into your database."
log_warn "Make sure the tables are empty or you may get duplicate key errors."
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Aborted."
    rm -rf "$TEMP_DIR"
    exit 0
fi

# Restore each table in order
for table in "${TABLES[@]}"; do
    json_file="${BACKUP_DIR}/${table}.json"

    if [ ! -f "$json_file" ]; then
        log_warn "No backup file for table: ${table}, skipping..."
        continue
    fi

    record_count=$(jq 'length' "$json_file")

    if [ "$record_count" -eq 0 ]; then
        log_info "Table ${table}: 0 records, skipping..."
        continue
    fi

    log_info "Restoring table ${table}: ${record_count} records..."

    # Insert data using Supabase REST API
    response=$(curl -s -w "\n%{http_code}" \
        "${SUPABASE_URL}/rest/v1/${table}" \
        -H "apikey: ${SUPABASE_KEY}" \
        -H "Authorization: Bearer ${SUPABASE_KEY}" \
        -H "Content-Type: application/json" \
        -H "Prefer: resolution=ignore-duplicates" \
        -d @"$json_file")

    http_code=$(echo "$response" | tail -n1)

    if [ "$http_code" -eq 201 ] || [ "$http_code" -eq 200 ]; then
        log_info "  -> Success"
    else
        body=$(echo "$response" | sed '$d')
        log_error "  -> Failed (HTTP ${http_code})"
        log_error "  -> ${body}"
    fi
done

# Cleanup
rm -rf "$TEMP_DIR"

log_info "Restore complete!"
log_warn "You may need to reset sequences if using IDENTITY columns."
log_warn "Run this SQL in Supabase SQL Editor if needed:"
echo ""
echo "  SELECT setval(pg_get_serial_sequence('players', 'player_id'), COALESCE(MAX(player_id), 1)) FROM players;"
echo "  SELECT setval(pg_get_serial_sequence('teams', 'team_id'), COALESCE(MAX(team_id), 1)) FROM teams;"
echo "  SELECT setval(pg_get_serial_sequence('matches', 'match_id'), COALESCE(MAX(match_id), 1)) FROM matches;"
echo ""
