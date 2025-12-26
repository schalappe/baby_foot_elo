# Operations Documentation

## Overview

This directory contains operational guides for deployment, backup, testing, and maintenance of the Baby Foot ELO application.

## Documents

### [Database Backup](./database-backup.md)
**Purpose**: Automated database backup and restoration system

**Contents**:
- GitHub Actions automated daily backups
- Manual local backup scripts
- Restoration procedures (using `psql`)
- Troubleshooting guide
- Security considerations

**Key Commands**:
```bash
# Local backup
./scripts/backup_supabase.sh

# Restore from backup
export DATABASE_URL="postgresql://..."
./scripts/restore_supabase.sh backups/backup_YYYYMMDD_HHMMSS.tar.gz
```

**Backup Schedule**: Daily at 2:00 AM UTC (GitHub Actions)
**Retention**: 30 days in GitHub Artifacts

---

### [Local Testing](./local-testing.md)
**Purpose**: Guide for running tests with local Supabase instance

**Contents**:
- Local Supabase setup with Docker
- Test environment configuration
- Running integration and unit tests
- Database migration management
- Troubleshooting test failures

**Key Commands**:
```bash
# All-in-one test (CI-friendly)
bun run test:local

# Manual workflow
bun run supabase:start   # Start local Supabase
bun run test             # Run tests in watch mode
bun run supabase:stop    # Stop when done
```

**Local Services**: API (54321), Database (54322), Studio (54323)

---

## Quick Reference

### Backup & Restore

#### Create Backup (Local)
```bash
export SUPABASE_URL="https://xxx.supabase.co"
export SUPABASE_KEY="sb_publishable_..."
./scripts/backup_supabase.sh
```

#### Restore Backup
```bash
export DATABASE_URL="postgresql://postgres:password@db.xxx.supabase.co:5432/postgres"
./scripts/restore_supabase.sh backups/backup_YYYYMMDD_HHMMSS.tar.gz
```

#### Access GitHub Backups
1. Go to repository → Actions
2. Click "Database Backup" workflow run
3. Download artifact from Artifacts section

---

### Local Testing

#### Start Local Supabase
```bash
bun run supabase:start
# Services available at http://localhost:54321 (API)
# Studio UI at http://localhost:54323
```

#### Run Tests
```bash
# With local Supabase already running
bun run test

# Automated (start, test, stop)
bun run test:local
```

#### Reset Database
```bash
bun run supabase:reset
# Drops all tables and re-applies migrations
```

---

## Operational Procedures

### Deployment Checklist

**Before Deploying**:
- [ ] Run full test suite: `bun run test:local`
- [ ] Lint code: `bun run lint`
- [ ] Format code: `bun run format`
- [ ] Build succeeds: `bun run build`
- [ ] Type check passes: `bun run typecheck`

**Deploy to Vercel**:
```bash
# Automatic deployment on push to main branch
git push origin main

# Manual deployment via Vercel CLI
vercel deploy --prod
```

**After Deploying**:
- [ ] Verify application loads
- [ ] Test player registration
- [ ] Test match recording
- [ ] Check rankings display
- [ ] Verify database connectivity

---

### Database Maintenance

#### Apply Migration to Production

1. **Test Locally**:
   ```bash
   supabase migration new migration_name
   # Edit migration file
   bun run supabase:reset
   # Test thoroughly
   ```

2. **Push to Production**:
   ```bash
   # Via Supabase Dashboard
   # Settings → Database → Migrations → Run migration

   # Or via CLI (if configured)
   supabase db push
   ```

3. **Verify**:
   - Check Supabase Dashboard → Database → Tables
   - Test affected API endpoints
   - Monitor error logs

#### Backup Before Major Changes

```bash
# Create manual backup before risky operations
export SUPABASE_URL="..."
export SUPABASE_KEY="..."
./scripts/backup_supabase.sh
```

---

### Monitoring

#### Check Application Health

```bash
# Health check endpoint
curl https://your-domain.vercel.app/api/v1/health
```

**Expected Response**:
```json
{
  "status": "ok",
  "timestamp": "2025-12-26T19:30:00Z"
}
```

#### Monitor Logs

**Vercel Logs**:
- Dashboard → Project → Logs
- Filter by function, status code, or time range

**Supabase Logs**:
```bash
# Via MCP server (if configured)
supabase get_logs --service api
supabase get_logs --service postgres
```

---

### Troubleshooting

#### Common Production Issues

| Issue | Diagnosis | Solution |
|-------|-----------|----------|
| **500 errors on API calls** | Check Vercel function logs | Verify env variables, check database connectivity |
| **Database connection timeout** | Supabase Dashboard → Database | Check connection pooling, upgrade plan if needed |
| **Slow rankings page** | Check RPC function performance | Verify indexes exist, consider caching |
| **Missing players in rankings** | Data integrity issue | Check RPC function query, verify data in tables |

#### Emergency Procedures

**Data Loss (Accidental Deletion)**:
1. Stop all write operations
2. Download latest backup from GitHub Actions
3. Restore using `restore_supabase.sh`
4. Verify data integrity
5. Resume normal operations

**Application Down**:
1. Check Vercel status page
2. Verify Supabase is operational
3. Review recent deployments
4. Rollback if needed (Vercel Dashboard → Deployments → Redeploy previous)

**Database Corruption**:
1. Identify when corruption occurred
2. Restore from backup before corruption
3. Manually recreate data added after backup
4. Investigate root cause

---

## Security

### Environment Variables

**Required Variables**:
- `NEXT_PUBLIC_SUPABASE_URL` - Supabase project URL
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` - Supabase publishable key (preferred)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Supabase anon key (fallback for local)

**Secret Management**:
- ✅ **DO**: Store secrets in Vercel environment variables
- ✅ **DO**: Use `.env.local` for local development (git-ignored)
- ❌ **DON'T**: Commit secrets to repository
- ❌ **DON'T**: Use production credentials in development

### Backup Security

- Backup files contain all database data (plaintext JSON)
- Store backups securely, delete when no longer needed
- Use `DATABASE_URL` (not REST API) for restores
- Protect database password (full database access)

---

## Performance Optimization

### Database Query Performance

**RPC Function Optimization**:
- Use CTEs for complex aggregations (41x faster)
- Add indexes on foreign keys and frequently queried columns
- Monitor query execution time in Supabase Dashboard

**Example Slow Query Fix**:
```sql
-- Before: N+1 queries
SELECT * FROM players;
-- Then fetch stats for each player (N queries)

-- After: Single RPC with CTE
SELECT * FROM get_all_players_with_stats_optimized();
-- One query returns all data
```

### Frontend Caching

**SWR Configuration**:
```typescript
useSWR('/api/v1/players/rankings', fetcher, {
  refreshInterval: 30000,  // 30 seconds
  revalidateOnFocus: false // Don't refetch on tab focus
});
```

**Optimization Tips**:
- Cache rankings for 30 seconds (reduces API load)
- Use skeleton loaders for perceived performance
- Lazy load player details (don't fetch on rankings page)

---

## Cost Management

### Current Costs (Free Tier)

| Service | Plan | Cost |
|---------|------|------|
| **Vercel** | Hobby | $0/month |
| **Supabase** | Free | $0/month |
| **GitHub Actions** | Free (2,000 min) | $0/month |
| **Total** | | **$0/month** |

### Usage Limits

**Supabase Free Tier**:
- 500 MB database storage
- 2 GB egress bandwidth/month
- 500,000 API requests/month

**Vercel Hobby**:
- 100 GB bandwidth/month
- 100,000 function invocations/month

**Monitoring**:
- Check Supabase Dashboard → Usage
- Check Vercel Dashboard → Analytics → Usage

### Scaling Considerations

**When to Upgrade**:
- Database > 400 MB → Supabase Pro ($25/month)
- > 10,000 matches/month → Consider Pro for better performance
- > 50 concurrent users → Upgrade Vercel to Pro ($20/month)

---

## Disaster Recovery

### Backup Strategy

**3-2-1 Rule**:
- **3 copies**: Production DB + GitHub Artifacts + Local backup
- **2 media types**: Cloud (GitHub) + Local disk
- **1 offsite**: GitHub (separate from Supabase)

**Recovery Time Objectives**:
- **RTO** (Recovery Time Objective): < 1 hour
- **RPO** (Recovery Point Objective): < 24 hours (daily backups)

### Disaster Scenarios

**Scenario 1**: Supabase outage
- **Impact**: Application down, no data access
- **Recovery**: Wait for Supabase restoration, or migrate to new Supabase project

**Scenario 2**: Accidental data deletion
- **Impact**: Missing data, users affected
- **Recovery**: Restore from latest backup (~5 minutes)

**Scenario 3**: Vercel deployment failure
- **Impact**: Application unreachable
- **Recovery**: Rollback to previous deployment via Vercel Dashboard

---

## Related Documentation

### For Development
→ [Technical Documentation](../technical/README.md)

### For Architecture
→ [Architecture Overview](../technical/01-architecture-overview.md)

### For Product Context
→ [Product Documentation](../product/README.md)

---

## Maintenance Schedule

### Daily
- ✅ Automated database backup (2 AM UTC)
- ✅ Monitor error logs (Vercel + Supabase)

### Weekly
- Review usage metrics (Supabase Dashboard)
- Check backup success (GitHub Actions)
- Review performance metrics

### Monthly
- Review and clean old backups (>30 days)
- Update dependencies: `bun update`
- Security audit: Check for CVEs

### Quarterly
- Review scaling needs
- Performance optimization review
- Documentation updates

---

**Last Updated**: 2025-12-26
**Maintained By**: Operations Team
