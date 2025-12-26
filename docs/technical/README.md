# Technical Documentation

## Overview

This directory contains comprehensive technical documentation for the Baby Foot ELO application. Each document focuses on a specific aspect of the system architecture, design, and implementation.

## Documentation Index

### Core Architecture

1. **[Architecture Overview](./01-architecture-overview.md)** 📐
   - High-level system architecture
   - Layered architecture breakdown (Frontend → API → Service → Repository → Database)
   - Technology stack and design patterns
   - Performance and security considerations
   - **Start here** for understanding the overall system design

2. **[Database Schema](./02-database-schema.md)** 🗄️
   - Complete database structure and ERD
   - Table definitions with constraints
   - RPC function documentation
   - Query performance optimization
   - Migration strategy

3. **[Sequence Diagrams](./03-sequence-diagrams.md)** 📊
   - Match creation flow (9-step process)
   - Player rankings retrieval
   - Player detail page load
   - New player registration with auto-team creation
   - Match history filtering (frontend)
   - Error handling and retry logic

### Business Logic

4. **[ELO Calculation System](./04-elo-calculation-system.md)** 🎯
   - Hybrid ELO algorithm explanation
   - K-factor tiers (200/100/50)
   - Pool correction for zero-sum enforcement
   - Win probability calculation
   - Worked examples with step-by-step math

5. **[Service Layer Documentation](./05-service-layer.md)** ⚙️
   - Service pattern implementation
   - Business logic organization
   - Match orchestration (matches.ts)
   - Player/team lifecycle management
   - Service dependencies and composition

6. **[Repository Layer](./06-repository-layer.md)** 💾
   - Repository pattern implementation
   - Database access abstraction
   - Retry logic with exponential backoff
   - RPC function calls
   - Batch operations for performance

### API Documentation

7. **[API Reference](./07-api-reference.md)** 🔌
   - Complete REST API endpoint documentation
   - Request/response schemas
   - Error codes and handling
   - Rate limiting and caching
   - Authentication (future)

### Frontend Architecture

8. **[Frontend Architecture](./08-frontend-architecture.md)** 🎨
   - Component hierarchy and organization
   - SWR data fetching patterns
   - State management strategy
   - UI component library (ShadCN)
   - Performance optimizations

9. **[Component Documentation](./09-component-reference.md)** 🧩
   - Individual component documentation
   - Props and interfaces
   - Usage examples
   - Reusable patterns

### Deployment & Operations

10. **[Deployment Guide](./10-deployment-guide.md)** 🚀
    - Environment setup
    - Vercel deployment configuration
    - Supabase configuration
    - Environment variables
    - Monitoring and logging

## Quick Start for Developers

### Understanding the System

**New to the codebase?** Read in this order:
1. [Architecture Overview](./01-architecture-overview.md) - Get the big picture
2. [Database Schema](./02-database-schema.md) - Understand data structure
3. [Sequence Diagrams](./03-sequence-diagrams.md) - See how it all works together

### Working on Specific Areas

**Frontend Development**:
- [Frontend Architecture](./08-frontend-architecture.md)
- [Component Documentation](./09-component-reference.md)
- [API Reference](./07-api-reference.md) (for API integration)

**Backend Development**:
- [Service Layer Documentation](./05-service-layer.md)
- [Repository Layer](./06-repository-layer.md)
- [Database Schema](./02-database-schema.md)

**ELO Algorithm**:
- [ELO Calculation System](./04-elo-calculation-system.md)
- [Sequence Diagrams](./03-sequence-diagrams.md) (Match Creation Flow)

**Deployment & DevOps**:
- [Deployment Guide](./10-deployment-guide.md)
- [API Reference](./07-api-reference.md) (for endpoint configuration)

## Documentation Standards

### Maintenance

Each document includes:
- **Document Information**: Type, audience, last updated, maintainer
- **Maintenance Notes**: When to update the document
- **Related Documentation**: Links to related docs

### When to Update

Update documentation when:
- Adding new features or components
- Changing architecture or design patterns
- Modifying database schema
- Updating API endpoints
- Refactoring major code sections

### How to Update

1. Read the document's "Maintenance Notes" section
2. Update relevant sections with clear, concise changes
3. Update "Last Updated" date
4. Add links to related documentation if needed
5. Commit with message: `docs: update [document-name] for [feature/change]`

## Diagrams and Visual Aids

### ASCII Diagrams

All diagrams use ASCII art for:
- Portability (viewable in any text editor)
- Version control friendly (git diff works)
- No external tools required
- Fast to update

### Code Examples

All code examples:
- Use actual code from the codebase (not pseudo-code)
- Include file path references
- Show complete, runnable snippets where possible

## Contributing to Documentation

### Style Guide

- **Be Concise**: Short sentences, active voice
- **Be Specific**: Reference actual files (lib/services/elo.ts:45)
- **Be Clear**: Explain "why" not just "what"
- **Be Visual**: Use tables, diagrams, code blocks

### Example Documentation Pattern

```markdown
## Component Name

**Purpose**: Brief one-line description

**Location**: `path/to/file.ts`

**Key Functions**:
- `functionName()` - Description
- `anotherFunction()` - Description

**Example Usage**:
```typescript
// Actual code example
const result = functionName(params);
```

**Dependencies**:
- DependencyA (what it does)
- DependencyB (what it does)
```

## Related Resources

### External Documentation
- [Next.js Documentation](https://nextjs.org/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [SWR Documentation](https://swr.vercel.app/)
- [TanStack Table](https://tanstack.com/table/latest)

### Internal Documentation
- [Project README](../../README.md) - Setup and getting started
- [CLAUDE.md](../../CLAUDE.md) - Project overview for Claude Code
- [Product Documentation](../product/) - Product specs and roadmap

## Document Status

| Document | Status | Coverage |
|----------|--------|----------|
| 01-architecture-overview.md | ✅ Complete | 100% |
| 02-database-schema.md | ✅ Complete | 100% |
| 03-sequence-diagrams.md | ✅ Complete | 100% |
| 04-elo-calculation-system.md | 🚧 In Progress | 0% |
| 05-service-layer.md | 📝 Planned | 0% |
| 06-repository-layer.md | 📝 Planned | 0% |
| 07-api-reference.md | 📝 Planned | 0% |
| 08-frontend-architecture.md | 📝 Planned | 0% |
| 09-component-reference.md | 📝 Planned | 0% |
| 10-deployment-guide.md | 📝 Planned | 0% |

---

**Last Updated**: 2025-12-26
**Maintained By**: Development Team
**Questions?** Create an issue or reach out to the development team.
