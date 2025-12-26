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

5. **[Service Layer Documentation](./05-service-layer.md)** ⚙️ **NEW**
   - Complete class reference for all services
   - ELO Service: Pure calculation functions with formulas
   - Match Service: Match orchestration and ELO application (9-step flow)
   - Player Service: Lifecycle management and auto-team creation
   - Team Service: Team normalization and active rankings
   - Function signatures, parameters, return types, examples
   - Design patterns and testing strategies

6. **[Repository Layer](./06-repository-layer.md)** 💾 **NEW**
   - Complete class reference for all repositories
   - Player Repository: CRUD operations and ELO history
   - Team Repository: Player ID normalization pattern
   - Match Repository: Match creation and filtering
   - Stats Repository: RPC-based statistics aggregation
   - Retry wrapper with exponential backoff
   - Batch operations and performance optimization
   - Testing patterns for integration tests

7. **[Class Diagrams and Relationships](./07-class-diagrams.md)** 📊 **NEW**
   - System-wide architecture diagram (all layers)
   - Service layer class diagram with dependencies
   - Repository layer class diagram
   - Domain model (ERD with relationships)
   - Type system class hierarchy
   - Component hierarchy and composition
   - API route handler structure
   - Match creation sequence diagram
   - Player rankings data flow
   - ELO calculation flow chart
   - Error handling flow
   - 13 comprehensive Mermaid diagrams

### API Documentation

8. **[API Reference](./08-api-reference.md)** 🔌
   - Complete REST API endpoint documentation
   - Request/response schemas
   - Error codes and handling
   - Rate limiting and caching
   - Authentication (future)

### Frontend Architecture

9. **[Frontend Architecture](./09-frontend-architecture.md)** 🎨
   - Component hierarchy and organization
   - SWR data fetching patterns
   - State management strategy
   - UI component library (ShadCN)
   - Performance optimizations

10. **[Component Documentation](./10-component-reference.md)** 🧩
    - Individual component documentation
    - Props and interfaces
    - Usage examples
    - Reusable patterns

### Deployment & Operations

11. **[Deployment Guide](./11-deployment-guide.md)** 🚀
    - Environment setup
    - Vercel deployment configuration
    - Supabase configuration
    - Environment variables
    - Monitoring and logging

## Quick Start for Developers

### Understanding the System

**New to the codebase?** Read in this order:
1. [Architecture Overview](./01-architecture-overview.md) - Get the big picture (20 min)
2. [Class Diagrams](./07-class-diagrams.md) - Visual overview of all components (15 min)
3. [Database Schema](./02-database-schema.md) - Understand data structure (10 min)
4. [Sequence Diagrams](./03-sequence-diagrams.md) - See how it all works together (10 min)

**Deep dive into specific layers**:
- [Service Layer](./05-service-layer.md) - Business logic and orchestration
- [Repository Layer](./06-repository-layer.md) - Data access patterns

### Working on Specific Areas

**Frontend Development**:
- [Class Diagrams](./07-class-diagrams.md) - Component hierarchy section
- [Frontend Architecture](./09-frontend-architecture.md)
- [Component Documentation](./10-component-reference.md)
- [API Reference](./08-api-reference.md) (for API integration)

**Backend Development**:
- [Service Layer Documentation](./05-service-layer.md) - Complete class reference
- [Repository Layer](./06-repository-layer.md) - Complete class reference
- [Class Diagrams](./07-class-diagrams.md) - Service & repository diagrams
- [Database Schema](./02-database-schema.md)

**ELO Algorithm**:
- [Service Layer - ELO Service](./05-service-layer.md#elo-service-libserviceselots) - Function reference
- [ELO Calculation System](./04-elo-calculation-system.md) - Algorithm details
- [Class Diagrams](./07-class-diagrams.md#elo-calculation-flow-diagram) - Visual flow
- [Sequence Diagrams](./03-sequence-diagrams.md) (Match Creation Flow)

**Deployment & DevOps**:
- [Deployment Guide](./11-deployment-guide.md)
- [API Reference](./08-api-reference.md) (for endpoint configuration)

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

| Document | Status | Coverage | Lines |
|----------|--------|----------|-------|
| 01-architecture-overview.md | ✅ Complete | 100% | 521 |
| 02-database-schema.md | ✅ Complete | 100% | 575 |
| 03-sequence-diagrams.md | ✅ Complete | 100% | 644 |
| 04-elo-calculation-system.md | ✅ Complete | 100% | 682 |
| 05-service-layer.md | ✅ Complete | 100% | 1,328 |
| 06-repository-layer.md | ✅ Complete | 100% | 1,127 |
| 07-class-diagrams.md | ✅ Complete | 100% | 867 |
| 08-api-reference.md | 📝 Planned | 0% | - |
| 09-frontend-architecture.md | 📝 Planned | 0% | - |
| 10-component-reference.md | 📝 Planned | 0% | - |
| 11-deployment-guide.md | 📝 Planned | 0% | - |

**Total Documentation**: 5,744+ lines across 7 comprehensive documents

---

## Documentation Metrics

**Coverage by Layer**:
- ✅ Architecture & Design: 100% (Architecture, Class Diagrams, Sequence Diagrams)
- ✅ Database Layer: 100% (Schema, RPC Functions)
- ✅ Repository Layer: 100% (Complete class reference)
- ✅ Service Layer: 100% (Complete class reference)
- ✅ Business Logic: 100% (ELO Calculation System)
- 🚧 API Layer: Planned (API Reference)
- 🚧 Frontend Layer: Planned (Frontend Architecture, Component Reference)
- 🚧 Operations: Planned (Deployment Guide)

**Documentation Quality**:
- All code examples reference actual file paths
- All functions include: purpose, parameters, returns, examples
- All diagrams use Mermaid for visualization
- All documents cross-reference related docs

---

**Last Updated**: 2025-12-26
**Maintained By**: Development Team
**Questions?** Create an issue or reach out to the development team.
