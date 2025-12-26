# Product Documentation

## Overview

This directory contains product-level documentation defining what Baby Foot ELO is, who it's for, and where it's headed.

## Documents

### [Mission](./mission.md)
**Purpose**: Product vision and value proposition

**Contents**:
- Product pitch and elevator summary
- Target users and personas
- Problem statement and our solution
- Key differentiators (hybrid ELO, pool correction, K-factor tiers)
- Core feature list

**Read this to**: Understand the product strategy and target market

---

### [Roadmap](./roadmap.md)
**Purpose**: Feature development plan and priorities

**Contents**:
- Current version features
- Planned features by phase
- Long-term vision
- Feature prioritization rationale

**Read this to**: See what's being built next and why

---

### [Tech Stack](./tech-stack.md)
**Purpose**: Technology choices and justification

**Contents**:
- Frontend stack (Next.js, React, Tailwind)
- Backend stack (Next.js API routes, PostgreSQL)
- Infrastructure (Vercel, Supabase)
- Rationale for each technology choice
- Trade-offs considered

**Read this to**: Understand technology decisions and constraints

---

## Quick Reference

### Target Users
1. **Office Teams**: Companies with foosball tables (casual competition)
2. **Foosball Clubs**: Recreational clubs (organized tournaments)

### Key Features
- Hybrid ELO system (individual + team ratings)
- Zero-sum pool correction (fair ELO economy)
- K-factor tiers (200/100/50 for progression)
- Real-time rankings and statistics
- Match history with ELO changes

### Differentiators vs Competitors
1. **Hybrid ELO**: Both individual and team ratings tracked independently
2. **Pool Correction**: Ensures no ELO inflation over time
3. **Progressive K-Factors**: Fast advancement for beginners, stable rankings for pros
4. **Free & Open Source**: No subscription fees

---

## Related Documentation

### For Implementation Details
→ [Technical Documentation](../technical/README.md)

### For Operations
→ [Operations Documentation](../operations/README.md)

### For Development Setup
→ [Developer Onboarding](../README.md#developer-onboarding)

---

## Updating Product Documentation

### When to Update

| Change | Document to Update |
|--------|-------------------|
| New feature idea | Roadmap (add to backlog) |
| Feature priority change | Roadmap (reorder phases) |
| New technology adoption | Tech Stack (add rationale) |
| Target audience shift | Mission (update personas) |
| Value proposition change | Mission (update differentiators) |

### Maintenance Checklist

Product documentation should be reviewed:
- [ ] After major feature releases
- [ ] When pivoting product direction
- [ ] Before fundraising or partnerships
- [ ] Quarterly for accuracy

---

## Product Metrics

### Current Status
- **Version**: 1.0 (MVP)
- **Users**: Office teams and clubs
- **Deployment**: Vercel + Supabase

### Success Metrics (Proposed)
- Number of active players
- Matches recorded per week
- User retention (players still active after 30 days)
- Match frequency (avg matches per player per week)

---

**Last Updated**: 2025-12-26
**Maintained By**: Product Team
