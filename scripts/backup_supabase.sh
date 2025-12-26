#!/bin/bash
# Supabase Data Backup Script
# Exports all tables to JSON files for easy restoration

set -e

# Configuration - these will be overridden by environment variables
# ##>: Use publishable key (sb_publishable_...) for production, anon key for local.
SUPABASE_URL="${SUPABASE_URL:-}"
SUPABASE_KEY="${SUPABASE_KEY:-}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"

# ##>: Supabase REST API has a default limit of 1000 rows per request.
PAGE_SIZE=1000

# Tables to backup (in order for proper restoration due to foreign keys)
TABLES=("players" "teams" "matches" "players_elo_history" "teams_elo_history")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Fetch all records from a table with pagination
# ##>: Supabase REST API limits responses to 1000 rows by default.
# ##>: This function paginates through all data using limit/offset.
fetch_all_records() {
    local table=$1
    local offset=0
    local all_records="[]"
    local page_count=0

    while true; do
        # Fetch a page of records
        response=$(curl -s -w "\n%{http_code}" \
            "${SUPABASE_URL}/rest/v1/${table}?select=*&limit=${PAGE_SIZE}&offset=${offset}" \
            -H "apikey: ${SUPABASE_KEY}" \
            -H "Authorization: Bearer ${SUPABASE_KEY}")

        http_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | sed '$d')

        if [ "$http_code" -ne 200 ]; then
            echo "ERROR:${http_code}:${body}"
            return 1
        fi

        # Count records in this page
        page_records=$(echo "$body" | jq 'length')

        if [ "$page_records" -eq 0 ]; then
            break
        fi

        # Merge this page into all_records
        all_records=$(echo "$all_records" "$body" | jq -s 'add')
        page_count=$((page_count + 1))

        # If we got fewer records than PAGE_SIZE, we've reached the end
        if [ "$page_records" -lt "$PAGE_SIZE" ]; then
            break
        fi

        offset=$((offset + PAGE_SIZE))
    done

    # Output the combined records
    echo "$all_records"
}

# Validate required environment variables
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    log_error "SUPABASE_URL and SUPABASE_KEY environment variables are required"
    echo "Usage: SUPABASE_URL=xxx SUPABASE_KEY=xxx ./backup_supabase.sh"
    exit 1
fi

# Create backup directory with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="${BACKUP_DIR}/${TIMESTAMP}"
mkdir -p "$BACKUP_PATH"

log_info "Starting backup to ${BACKUP_PATH}"

# Backup each table
for table in "${TABLES[@]}"; do
    log_info "Backing up table: ${table}"

    # Fetch all data with pagination
    result=$(fetch_all_records "$table")

    # Check for errors (result starts with "ERROR:")
    if [[ "$result" == ERROR:* ]]; then
        http_code=$(echo "$result" | cut -d: -f2)
        error_body=$(echo "$result" | cut -d: -f3-)
        log_error "Failed to backup ${table} (HTTP ${http_code})"
        echo "$error_body" > "${BACKUP_PATH}/${table}_error.json"
    else
        echo "$result" > "${BACKUP_PATH}/${table}.json"
        record_count=$(echo "$result" | jq 'length')
        log_info "  -> ${record_count} records saved"
    fi
done

# Create metadata file
cat > "${BACKUP_PATH}/metadata.json" << EOF
{
    "timestamp": "${TIMESTAMP}",
    "date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "supabase_url": "${SUPABASE_URL}",
    "tables": $(printf '%s\n' "${TABLES[@]}" | jq -R . | jq -s .)
}
EOF

# Create a compressed archive
log_info "Creating compressed archive..."
tar -czf "${BACKUP_DIR}/backup_${TIMESTAMP}.tar.gz" -C "${BACKUP_DIR}" "${TIMESTAMP}"

# Clean up uncompressed directory
rm -rf "$BACKUP_PATH"

log_info "Backup complete: ${BACKUP_DIR}/backup_${TIMESTAMP}.tar.gz"

# Keep only last 10 backups to save space
log_info "Cleaning old backups (keeping last 10)..."
cd "$BACKUP_DIR"
ls -t backup_*.tar.gz 2>/dev/null | tail -n +11 | xargs -r rm -f

log_info "Done!"
