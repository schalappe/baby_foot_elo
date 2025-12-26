# Spec Requirements: Backend Migration (Python → TypeScript)

## Initial Description

Migrate the Python/FastAPI backend from Heroku to TypeScript/Next.js on Vercel. All 18 API endpoints should be ported to Next.js API Routes while maintaining identical functionality.

Reference document: `docs/specs/backend-migration.md`

## Requirements Discussion

### Questions & Answers

**Q1:** Migrate the entire FastAPI backend (all 18 endpoints) in a single effort, or phased migration?
**A:** Single effort — migrate all endpoints at once.

**Q2:** Maintain backward compatibility with old Heroku URL during transition?
**A:** No backward compatibility. Switch immediately to new API routes.

**Q3:** Use `SUPABASE_SERVICE_ROLE_KEY` for server-side operations?
**A:** Use existing anon key (`SUPABASE_KEY`). Service role key can be addressed later if RLS policies are added.

**Q4:** Include validation step comparing TypeScript ELO calculations against Python results?
**A:** Yes. More safety is preferred.

**Q5:** Keep Supabase RPC functions (SQL) unchanged?
**A:** Yes. SQL functions remain as-is.

**Q6:** Include end-to-end tests (frontend → API → Supabase)?
**A:** No. Unit tests for ELO service + integration tests for API routes only.

**Q7:** Include rollback plan for post-deployment issues?
**A:** No rollback plan needed.

**Q8:** Out of scope items?
**A:** Pure migration only. No new features, no schema changes, no auth, no dependency upgrades.

### Existing Code References

- No existing Next.js API routes in the codebase — this will be the first
- Python backend at `backend/app/` provides the source implementation
- Existing spec at `docs/specs/backend-migration.md` provides architecture mapping

### Follow-up Questions

**Q:** Use existing anon key or obtain service role key?
**A:** Use existing anon key. Address service role key later if needed.

## Visual Assets

### Files Found

No visual assets provided.

## Requirements Summary

### Functional Requirements

- Port all 18 FastAPI endpoints to Next.js Route Handlers
- Maintain exact API contract (same endpoints, request/response formats)
- Preserve ELO calculation logic with identical results (K-factors, pool correction)
- Keep Supabase RPC functions unchanged
- Update frontend to use relative API URLs (`/api/v1/...`)

### Technical Approach

| Component      | Source (Python)         | Target (TypeScript)     |
| -------------- | ----------------------- | ----------------------- |
| Endpoints      | FastAPI routers         | Next.js Route Handlers  |
| Validation     | Pydantic models         | Zod schemas             |
| Business logic | Services                | `lib/services/*.ts`     |
| Data access    | Repositories            | `lib/repositories/*.ts` |
| Exceptions     | Custom classes          | `lib/errors/*.ts`       |
| Retry logic    | `@with_retry` decorator | `withRetry()` HOF       |

### Testing Strategy

- **Unit tests:** ELO calculation functions (compare against Python results)
- **Integration tests:** API routes against Supabase
- **No end-to-end tests**

### Reusability Opportunities

- Supabase client already configured in frontend
- TypeScript types can be derived from existing Python Pydantic models
- Existing `docs/specs/backend-migration.md` provides detailed mapping

### Scope Boundaries

**In Scope:**

- All 18 API endpoints
- ELO service (pure calculation functions)
- Type definitions (Zod schemas)
- Database utilities (client, retry)
- Repositories (data access layer)
- Services (business logic)
- Error classes
- Unit tests for ELO
- Integration tests for API routes

**Out of Scope:**

- New features
- Database schema changes
- Authentication/authorization
- Row Level Security
- Frontend dependency upgrades
- End-to-end tests
- Rollback plan
- Backward compatibility period

### Technical Considerations

- Use existing `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- Zod is the only new dependency needed (`bun add zod`)
- Frontend API calls update from `NEXT_PUBLIC_API_URL` to relative URLs
- Heroku backend removed after successful deployment
