#!/bin/bash
# Supabase Data Restore Script
# Restores data from a backup archive using direct PostgreSQL connection

set -e

# Configuration
DATABASE_URL="${DATABASE_URL:-}"

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

# Check for required tools
if ! command -v psql &> /dev/null; then
    log_error "psql is required but not installed."
    log_error "Install PostgreSQL client: brew install libpq && brew link libpq --force"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    log_error "jq is required but not installed."
    exit 1
fi

# Validate arguments
if [ -z "$1" ]; then
    log_error "Usage: DATABASE_URL=xxx ./restore_supabase.sh <backup_file.tar.gz>"
    log_info ""
    log_info "Get your DATABASE_URL from Supabase Dashboard:"
    log_info "  Settings → Database → Connection string → URI"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    log_error "Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

# Validate environment variables
if [ -z "$DATABASE_URL" ]; then
    log_error "DATABASE_URL environment variable is required"
    log_info ""
    log_info "Get your DATABASE_URL from Supabase Dashboard:"
    log_info "  Settings → Database → Connection string → URI"
    exit 1
fi

# Test database connection
log_info "Testing database connection..."
if ! psql "$DATABASE_URL" -c "SELECT 1" &> /dev/null; then
    log_error "Failed to connect to database. Check your DATABASE_URL."
    exit 1
fi
log_info "Database connection successful."

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

# Function to generate INSERT SQL from JSON
generate_insert_sql() {
    local table="$1"
    local json_file="$2"
    local temp_sql="$3"

    # [>]: Use jq to generate complete SQL in one pass for correctness and performance.
    # Keys are sorted alphabetically by jq, so we extract values in the same order.
    jq -r '
        # Get sorted column names from first record
        (.[0] | keys) as $cols |

        # Build the INSERT statement header
        "INSERT INTO '"${table}"' (" + ($cols | join(", ")) + ") OVERRIDING SYSTEM VALUE VALUES",

        # Build each row values
        (.[] | [.[$cols[]]] |
            "(" + (
                map(
                    if . == null then "NULL"
                    elif type == "string" then "$$" + gsub("\\$\\$"; "$ $") + "$$"
                    elif type == "boolean" then (if . then "true" else "false" end)
                    else tostring
                    end
                ) | join(", ")
            ) + "),"
        )
    ' "$json_file" > "$temp_sql"

    # Remove trailing comma from last line and add semicolon
    sed -i '' '$ s/,$/;/' "$temp_sql"
}

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

    # Generate SQL file
    temp_sql="${TEMP_DIR}/${table}_insert.sql"
    generate_insert_sql "$table" "$json_file" "$temp_sql"

    # Execute SQL using psql
    if psql "$DATABASE_URL" -f "$temp_sql" &> /dev/null; then
        log_info "  -> Success"
    else
        log_error "  -> Failed to restore ${table}"
        # Show error details
        psql "$DATABASE_URL" -f "$temp_sql" 2>&1 | head -5
    fi
done

# Reset sequences for identity columns
log_info "Resetting identity sequences..."
psql "$DATABASE_URL" <<EOF
SELECT setval(pg_get_serial_sequence('players', 'player_id'), COALESCE(MAX(player_id), 1)) FROM players;
SELECT setval(pg_get_serial_sequence('teams', 'team_id'), COALESCE(MAX(team_id), 1)) FROM teams;
SELECT setval(pg_get_serial_sequence('matches', 'match_id'), COALESCE(MAX(match_id), 1)) FROM matches;
SELECT setval(pg_get_serial_sequence('players_elo_history', 'history_id'), COALESCE(MAX(history_id), 1)) FROM players_elo_history;
SELECT setval(pg_get_serial_sequence('teams_elo_history', 'history_id'), COALESCE(MAX(history_id), 1)) FROM teams_elo_history;
EOF

# Cleanup
rm -rf "$TEMP_DIR"

log_info "Restore complete!"
