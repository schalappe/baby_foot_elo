# Class Diagrams and Relationships

**Last Updated**: 2025-12-26
**Document Type**: Architecture Diagrams
**Target Audience**: Developers, Architects

---

## Overview

This document provides comprehensive class diagrams showing the relationships between all major components in the Baby Foot ELO system. The diagrams use Mermaid syntax for visualization.

---

## System-Wide Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        Pages[Pages<br/>app/**/*.tsx]
        Components[Components<br/>components/**/*.tsx]
        Hooks[Custom Hooks<br/>hooks/**/*.ts]
        APIClient[API Client<br/>lib/api/client/*.ts]
    end

    subgraph "Backend Layer - API Routes"
        PlayersAPI[Players API<br/>app/api/v1/players]
        TeamsAPI[Teams API<br/>app/api/v1/teams]
        MatchesAPI[Matches API<br/>app/api/v1/matches]
    end

    subgraph "Service Layer"
        PlayerService[Player Service<br/>lib/services/players.ts]
        TeamService[Team Service<br/>lib/services/teams.ts]
        MatchService[Match Service<br/>lib/services/matches.ts]
        EloService[ELO Service<br/>lib/services/elo.ts]
    end

    subgraph "Repository Layer"
        PlayerRepo[Player Repository<br/>lib/db/repositories/players.ts]
        TeamRepo[Team Repository<br/>lib/db/repositories/teams.ts]
        MatchRepo[Match Repository<br/>lib/db/repositories/matches.ts]
        StatsRepo[Stats Repository<br/>lib/db/repositories/stats.ts]
        HistoryRepo[History Repository<br/>lib/db/repositories/elo-history.ts]
    end

    subgraph "Database Layer"
        Players[(Players Table)]
        Teams[(Teams Table)]
        Matches[(Matches Table)]
        PlayerHistory[(Players ELO History)]
        TeamHistory[(Teams ELO History)]
        RPC[RPC Functions<br/>SQL stored procedures]
    end

    %% Frontend connections
    Pages --> Components
    Components --> Hooks
    Hooks --> APIClient
    APIClient -->|HTTP| PlayersAPI
    APIClient -->|HTTP| TeamsAPI
    APIClient -->|HTTP| MatchesAPI

    %% API to Service connections
    PlayersAPI --> PlayerService
    TeamsAPI --> TeamService
    MatchesAPI --> MatchService

    %% Service layer interactions
    PlayerService --> PlayerRepo
    PlayerService --> TeamRepo
    TeamService --> TeamRepo
    TeamService --> StatsRepo
    MatchService --> MatchRepo
    MatchService --> EloService
    MatchService --> PlayerRepo
    MatchService --> TeamRepo
    MatchService --> HistoryRepo

    %% Repository to Database
    PlayerRepo --> Players
    PlayerRepo --> RPC
    TeamRepo --> Teams
    TeamRepo --> RPC
    MatchRepo --> Matches
    MatchRepo --> RPC
    StatsRepo --> RPC
    HistoryRepo --> PlayerHistory
    HistoryRepo --> TeamHistory

    %% Styling
    classDef frontend fill:#e1f5ff
    classDef backend fill:#fff4e1
    classDef service fill:#e8f5e9
    classDef repo fill:#f3e5f5
    classDef db fill:#ffebee

    class Pages,Components,Hooks,APIClient frontend
    class PlayersAPI,TeamsAPI,MatchesAPI backend
    class PlayerService,TeamService,MatchService,EloService service
    class PlayerRepo,TeamRepo,MatchRepo,StatsRepo,HistoryRepo repo
    class Players,Teams,Matches,PlayerHistory,TeamHistory,RPC db
```

---

## Service Layer Class Diagram

```mermaid
classDiagram
    class EloService {
        <<pure functions>>
        +determineKFactor(currentElo: number): number
        +calculateTeamElo(p1Elo: number, p2Elo: number): number
        +calculateWinProbability(eloA: number, eloB: number): number
        +calculateEloChange(currentElo, expectedScore, actualScore): number
        +calculateEloChangesWithPoolCorrection(changes[]): Map
        +calculatePlayersEloChange(winnerTeam, loserTeam): Object
        +calculateTeamEloChange(winnerTeam, loserTeam): Object
        +processMatchResult(winnerTeam, loserTeam): ProcessedMatchResult
    }

    class PlayerService {
        +createNewPlayer(data: PlayerCreate): Promise~PlayerResponse~
        +getAllPlayersWithStats(limit?: number): Promise~PlayerResponse[]~
        +getPlayer(playerId: number): Promise~PlayerResponse~
        +updateExistingPlayer(playerId, data): Promise~PlayerResponse~
        +deletePlayer(playerId: number): Promise~void~
        +getPlayerEloHistory(playerId: number): Promise~EloHistoryResponse[]~
        -validatePlayerExists(playerId: number): Promise~void~
        -autoCreateTeams(newPlayerId: number): Promise~void~
    }

    class TeamService {
        +createNewTeam(data: TeamCreate): Promise~TeamResponse~
        +getAllTeamsWithStats(limit?: number): Promise~TeamResponse[]~
        +getActiveTeamRankings(limit?: number): Promise~TeamResponse[]~
        +getTeam(teamId: number): Promise~TeamResponse~
        +getTeamsByPlayer(playerId: number): Promise~TeamResponse[]~
        +updateExistingTeam(teamId, data): Promise~TeamResponse~
        +deleteTeam(teamId: number): Promise~void~
        -normalizePlayerIds(p1: number, p2: number): [number, number]
    }

    class MatchService {
        +createNewMatch(data: MatchCreate): Promise~MatchWithEloResponse~
        +getMatch(matchId: number): Promise~MatchResponse~
        +getMatches(options?): Promise~MatchResponse[]~
        +getMatchesByPlayer(playerId, options?): Promise~Object~
        +getMatchesWithTeamElo(teamId: number): Promise~TeamMatchHistory[]~
        +deleteMatch(matchId: number): Promise~void~
        -validateMatchTeams(winnerId, loserId): void
        -applyEloChanges(playerChanges, teamChanges): Promise~void~
    }

    %% Dependencies
    MatchService ..> EloService : uses
    MatchService ..> TeamService : uses (getTeam)
    PlayerService ..> TeamService : uses (createTeam)
```

---

## Repository Layer Class Diagram

```mermaid
classDiagram
    class PlayerRepository {
        +createPlayer(name: string, elo?: number): Promise~Player~
        +getPlayerById(playerId: number): Promise~Player~
        +getPlayerByName(name: string): Promise~Player | null~
        +getAllPlayers(): Promise~PlayerWithStatsRow[]~
        +updatePlayerElo(playerId, newElo): Promise~void~
        +batchUpdatePlayersElo(updates[]): Promise~void~
        +updatePlayer(playerId, updates): Promise~Player~
        +deletePlayerById(playerId): Promise~void~
        +recordPlayerEloHistory(...): Promise~void~
        +getPlayerEloHistory(playerId): Promise~PlayerEloHistoryRow[]~
    }

    class TeamRepository {
        +normalizePlayerIds(p1, p2): [number, number]
        +createTeamByPlayerIds(p1, p2, elo?): Promise~Team~
        +getTeamById(teamId: number): Promise~Team | null~
        +getTeamByPlayerIds(p1, p2): Promise~Team | null~
        +getAllTeams(): Promise~TeamWithStatsRow[]~
        +getTeamsByPlayerId(playerId): Promise~TeamWithStatsRow[]~
        +getActiveTeamsWithStats(min, days): Promise~TeamWithStatsRow[]~
        +updateTeamElo(teamId, newElo): Promise~void~
        +batchUpdateTeamsElo(updates[]): Promise~void~
        +deleteTeamById(teamId): Promise~void~
        +recordTeamEloHistory(...): Promise~void~
    }

    class MatchRepository {
        +createMatchByTeamIds(winner, loser, ...): Promise~number~
        +getMatchById(matchId: number): Promise~Match | null~
        +getAllMatches(options?): Promise~any[]~
        +getMatchesByTeamId(teamId): Promise~any[]~
        +getMatchesByPlayerId(playerId, limit?, offset?): Promise~Object~
        +deleteMatchById(matchId): Promise~void~
    }

    class StatsRepository {
        +getPlayerStats(playerId: number): Promise~PlayerStatsRow | null~
        +getTeamStats(teamId: number): Promise~TeamStatsRow | null~
    }

    class EloHistoryRepository {
        +getPlayerEloHistory(playerId): Promise~PlayerEloHistoryRow[]~
        +getTeamEloHistory(teamId): Promise~TeamEloHistoryRow[]~
    }

    class SupabaseClient {
        <<singleton>>
        +from(table: string): QueryBuilder
        +rpc(functionName: string, params?): Promise
    }

    %% All repositories use Supabase client
    PlayerRepository ..> SupabaseClient : uses
    TeamRepository ..> SupabaseClient : uses
    MatchRepository ..> SupabaseClient : uses
    StatsRepository ..> SupabaseClient : uses
    EloHistoryRepository ..> SupabaseClient : uses
```

---

## Domain Model (Database Entities)

```mermaid
erDiagram
    PLAYERS ||--o{ PLAYERS_ELO_HISTORY : "has history"
    PLAYERS ||--o{ TEAMS : "is in (as player1)"
    PLAYERS ||--o{ TEAMS : "is in (as player2)"
    TEAMS ||--o{ TEAMS_ELO_HISTORY : "has history"
    TEAMS ||--o{ MATCHES : "wins"
    TEAMS ||--o{ MATCHES : "loses"
    MATCHES ||--o{ PLAYERS_ELO_HISTORY : "causes"
    MATCHES ||--o{ TEAMS_ELO_HISTORY : "causes"

    PLAYERS {
        int player_id PK
        string name UNIQUE
        int global_elo
        timestamp created_at
    }

    TEAMS {
        int team_id PK
        int player1_id FK
        int player2_id FK
        int global_elo
        timestamp created_at
        timestamp last_match_at
    }

    MATCHES {
        int match_id PK
        int winner_team_id FK
        int loser_team_id FK
        boolean is_fanny
        timestamp played_at
        text notes
    }

    PLAYERS_ELO_HISTORY {
        int history_id PK
        int player_id FK
        int match_id FK
        int old_elo
        int new_elo
        int difference
        timestamp date
    }

    TEAMS_ELO_HISTORY {
        int history_id PK
        int team_id FK
        int match_id FK
        int old_elo
        int new_elo
        int difference
        timestamp date
    }
```

---

## Type System Class Diagram

```mermaid
classDiagram
    %% Domain Types
    class Player {
        +player_id: number
        +name: string
        +global_elo: number
        +created_at: string
    }

    class Team {
        +team_id: number
        +player1_id: number
        +player2_id: number
        +global_elo: number
        +created_at: string
        +last_match_at?: string
    }

    class Match {
        +match_id: number
        +winner_team_id: number
        +loser_team_id: number
        +is_fanny: boolean
        +played_at: string
        +notes?: string
    }

    %% Response Schemas
    class PlayerResponse {
        +player_id: number
        +name: string
        +global_elo: number
        +matches_played?: number
        +wins?: number
        +losses?: number
        +win_rate?: number
        +rank?: number
        +last_match_at?: string
    }

    class TeamResponse {
        +team_id: number
        +player1_id: number
        +player2_id: number
        +global_elo: number
        +matches_played?: number
        +wins?: number
        +losses?: number
        +win_rate?: number
        +rank?: number
        +last_match_at?: string
    }

    class MatchResponse {
        +match_id: number
        +winner_team_id: number
        +loser_team_id: number
        +is_fanny: boolean
        +played_at: string
        +notes?: string
    }

    class MatchWithEloResponse {
        +match_id: number
        +winner_team_id: number
        +loser_team_id: number
        +is_fanny: boolean
        +played_at: string
        +notes?: string
        +elo_changes: Record~number, EloChange~
    }

    %% Create Schemas
    class PlayerCreate {
        +name: string
        +global_elo?: number
    }

    class TeamCreate {
        +player1_id: number
        +player2_id: number
        +global_elo?: number
    }

    class MatchCreate {
        +winner_team_id: number
        +loser_team_id: number
        +is_fanny: boolean
        +played_at: string
        +notes?: string
    }

    %% ELO Types
    class EloChange {
        +old_elo: number
        +new_elo: number
        +difference: number
    }

    class ProcessedMatchResult {
        +playerChanges: Map~number, EloChange~
        +teamChanges: Map~number, EloChange~
    }

    %% Relationships
    PlayerResponse --|> Player : extends
    TeamResponse --|> Team : extends
    MatchResponse --|> Match : extends
    MatchWithEloResponse --|> MatchResponse : extends
    MatchWithEloResponse *-- EloChange : contains
    ProcessedMatchResult *-- EloChange : contains
```

---

## Frontend Component Hierarchy

```mermaid
graph TB
    subgraph "Pages (Next.js App Router)"
        HomePage[page.tsx<br/>Player Rankings]
        PlayersListPage[players/page.tsx<br/>Players List]
        PlayerDetailPage[players/[id]/page.tsx<br/>Player Detail]
        TeamsListPage[teams/page.tsx<br/>Teams List]
        TeamDetailPage[teams/[id]/page.tsx<br/>Team Detail]
        MatchesPage[matches/page.tsx<br/>Match History]
    end

    subgraph "Feature Components - Players"
        PlayerRankingsDisplay[PlayerRankingsDisplay]
        PlayerRegistrationForm[PlayerRegistrationForm]
        PlayerDetail[PlayerDetail]
        PlayerMatchesSection[PlayerMatchesSection]
    end

    subgraph "Feature Components - Teams"
        TeamRankingsDisplay[TeamRankingsDisplay]
        TeamDetail[TeamDetail]
        TeamMatchesSection[TeamMatchesSection]
    end

    subgraph "Feature Components - Matches"
        NewMatchDialog[NewMatchDialog]
        NewMatchPage[NewMatchPage]
        MatchHistoryUI[MatchHistoryUI]
    end

    subgraph "Common Components"
        RankingTable[RankingTable]
        EntityStatsCards[EntityStatsCards]
        EntityMatchesSection[EntityMatchesSection]
    end

    subgraph "UI Primitives (ShadCN)"
        Button[Button]
        Dialog[Dialog]
        Table[Table]
        Card[Card]
        Form[Form]
    end

    %% Page to Component connections
    HomePage --> PlayerRankingsDisplay
    PlayersListPage --> PlayerRankingsDisplay
    PlayersListPage --> PlayerRegistrationForm
    PlayerDetailPage --> PlayerDetail
    PlayerDetailPage --> PlayerMatchesSection
    TeamsListPage --> TeamRankingsDisplay
    TeamDetailPage --> TeamDetail
    TeamDetailPage --> TeamMatchesSection
    MatchesPage --> MatchHistoryUI
    MatchesPage --> NewMatchDialog

    %% Component composition
    PlayerRankingsDisplay --> RankingTable
    PlayerDetail --> EntityStatsCards
    PlayerMatchesSection --> EntityMatchesSection
    TeamRankingsDisplay --> RankingTable
    TeamDetail --> EntityStatsCards
    TeamMatchesSection --> EntityMatchesSection
    NewMatchDialog --> NewMatchPage

    %% Common to UI primitive
    RankingTable --> Table
    EntityStatsCards --> Card
    NewMatchPage --> Form
    NewMatchPage --> Button
    NewMatchDialog --> Dialog
```

---

## API Route Handler Structure

```mermaid
graph LR
    subgraph "API Route Handlers"
        PlayersRoute["/api/v1/players/route.ts"]
        PlayerDetailRoute["/api/v1/players/[playerId]/route.ts"]
        PlayerStatsRoute["/api/v1/players/[playerId]/statistics/route.ts"]
        PlayerMatchesRoute["/api/v1/players/[playerId]/matches/route.ts"]

        TeamsRoute["/api/v1/teams/route.ts"]
        TeamDetailRoute["/api/v1/teams/[teamId]/route.ts"]

        MatchesRoute["/api/v1/matches/route.ts"]
        MatchDetailRoute["/api/v1/matches/[matchId]/route.ts"]
    end

    subgraph "Middleware & Utilities"
        HandleRequest[handleApiRequest<br/>Error wrapper]
        ZodValidation[Zod Schemas<br/>Input validation]
    end

    subgraph "Services"
        PlayerSvc[Player Service]
        TeamSvc[Team Service]
        MatchSvc[Match Service]
    end

    %% Routes use middleware
    PlayersRoute --> HandleRequest
    PlayerDetailRoute --> HandleRequest
    TeamsRoute --> HandleRequest
    MatchesRoute --> HandleRequest

    %% Routes validate with Zod
    PlayersRoute --> ZodValidation
    TeamsRoute --> ZodValidation
    MatchesRoute --> ZodValidation

    %% Routes call services
    PlayersRoute --> PlayerSvc
    PlayerDetailRoute --> PlayerSvc
    PlayerStatsRoute --> PlayerSvc
    PlayerMatchesRoute --> PlayerSvc

    TeamsRoute --> TeamSvc
    TeamDetailRoute --> TeamSvc

    MatchesRoute --> MatchSvc
    MatchDetailRoute --> MatchSvc
```

---

## Match Creation Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant UI as NewMatchPage
    participant API as POST /api/v1/matches
    participant MS as Match Service
    participant TS as Team Service
    participant ES as ELO Service
    participant MR as Match Repo
    participant PR as Player Repo
    participant TR as Team Repo
    participant HR as History Repo

    U->>UI: Select 4 players, winner, date
    UI->>UI: Validate 4 distinct players
    UI->>API: POST match data

    API->>API: Validate with Zod schema
    API->>MS: createNewMatch(data)

    MS->>MS: Validate winner ≠ loser
    MS->>TS: getTeam(winner_team_id)
    TS->>MS: Return winner team + players
    MS->>TS: getTeam(loser_team_id)
    TS->>MS: Return loser team + players

    MS->>MR: createMatchByTeamIds(...)
    MR->>MS: Return match_id

    MS->>ES: processMatchResult(winner, loser)
    ES->>ES: Calculate player ELO changes (4 players)
    ES->>ES: Apply pool correction (zero-sum)
    ES->>ES: Calculate team ELO changes (2 teams)
    ES->>ES: Apply pool correction
    ES->>MS: Return playerChanges + teamChanges

    MS->>PR: batchUpdatePlayersElo(playerChanges)
    PR->>MS: Done

    MS->>HR: recordPlayerEloHistory (4 records)
    HR->>MS: Done

    MS->>TR: batchUpdateTeamsElo(teamChanges)
    TR->>MS: Done

    MS->>HR: recordTeamEloHistory (2 records)
    HR->>MS: Done

    MS->>API: Return MatchWithEloResponse
    API->>UI: Return 201 + match data
    UI->>U: Display match result + ELO changes
```

---

## Data Flow: Player Rankings Display

```mermaid
sequenceDiagram
    participant U as User
    participant P as page.tsx
    participant SWR as useSWR Hook
    participant AC as API Client
    participant API as GET /api/v1/players/rankings
    participant PS as Player Service
    participant PR as Player Repo
    participant RPC as Supabase RPC

    U->>P: Visit homepage
    P->>SWR: useSWR(endpoint, getPlayerRankings)

    SWR->>AC: getPlayerRankings()
    AC->>API: GET /api/v1/players/rankings

    API->>PS: getAllPlayersWithStats()
    PS->>PR: getAllPlayers()
    PR->>RPC: get_all_players_with_stats_optimized()

    RPC->>RPC: Compute stats with CTE
    RPC->>PR: Return players with stats
    PR->>PS: Return PlayerWithStatsRow[]
    PS->>PS: Sort by ELO descending
    PS->>API: Return PlayerResponse[]

    API->>AC: Return JSON
    AC->>SWR: Return data
    SWR->>SWR: Cache data
    SWR->>P: Provide data + revalidate function

    P->>U: Render PlayerRankingsDisplay

    Note over SWR,AC: Auto-refresh every 30 seconds
    SWR->>AC: Revalidate (silent)
    AC->>API: GET /api/v1/players/rankings
    API->>SWR: Return updated data
    SWR->>P: Update UI
```

---

## ELO Calculation Flow Diagram

```mermaid
flowchart TD
    Start[Match Created: Winner Team vs Loser Team]

    Start --> CalcTeamElo1[Calculate Winner Team ELO<br/>avg of 2 player ELOs]
    CalcTeamElo1 --> CalcTeamElo2[Calculate Loser Team ELO<br/>avg of 2 player ELOs]

    CalcTeamElo2 --> WinProb[Calculate Win Probability<br/>P = 1 / 1 + 10^((ELO_B - ELO_A) / 400)]

    WinProb --> PlayerLoop{For each of 4 players}

    PlayerLoop --> DetermineK[Determine K-factor<br/>Based on player's current ELO]
    DetermineK --> CalcChange[Calculate ELO change<br/>K * (actual - expected)]
    CalcChange --> PlayerLoop

    PlayerLoop -->|All 4 done| PoolCorrect1[Sum all player changes]
    PoolCorrect1 --> CheckSum1{Sum = 0?}

    CheckSum1 -->|No| ApplyCorrection1[Apply pool correction<br/>Distribute difference proportionally]
    CheckSum1 -->|Yes| PlayerDone[Player ELO changes ready]
    ApplyCorrection1 --> PlayerDone

    PlayerDone --> TeamK1[Determine K-factor for winner team]
    TeamK1 --> TeamChange1[Calculate winner team change<br/>K * (1 - expected)]

    TeamChange1 --> TeamK2[Determine K-factor for loser team]
    TeamK2 --> TeamChange2[Calculate loser team change<br/>K * (0 - expected)]

    TeamChange2 --> PoolCorrect2[Apply pool correction to teams]
    PoolCorrect2 --> TeamDone[Team ELO changes ready]

    TeamDone --> Return[Return playerChanges Map<br/>+ teamChanges Map]
    Return --> End[Apply changes to database]
```

---

## Component Props Flow

```mermaid
graph TB
    subgraph "Player Detail Page"
        PDP[PlayerDetailPage<br/>Fetches player data]
    end

    subgraph "Player Detail Component"
        PDC[PlayerDetail<br/>Props: player]

        Stats[EntityStatsCards<br/>Props: stats object]
        Matches[PlayerMatchesSection<br/>Props: playerId]
    end

    subgraph "Generic Components"
        Table[Table<br/>Props: columns, data]
        Cards[Card components<br/>Props: title, value, trend]
    end

    %% Data flow
    PDP -->|player object| PDC
    PDC -->|stats extracted| Stats
    PDC -->|playerId| Matches

    Stats -->|array of stat objects| Cards
    Matches -->|matches array| Table

    %% Type annotations
    PDP -.->|PlayerResponse| PDC
    PDC -.->|PlayerStats| Stats
    PDC -.->|number| Matches
    Matches -.->|MatchWithEloChange[]| Table
```

---

## Error Handling Flow

```mermaid
flowchart TD
    Request[HTTP Request to API Route]

    Request --> Wrapper{handleApiRequest wrapper}

    Wrapper --> Handler[Route Handler Function]
    Handler --> Service[Service Function]
    Service --> Repo[Repository Function]

    Repo --> DBCall[Database Call]

    DBCall -->|Success| ReturnData[Return Data]
    DBCall -->|Error| RepoError{Error Type?}

    RepoError -->|Not Found| ThrowNotFound[Throw PlayerNotFoundError]
    RepoError -->|DB Error| ThrowDB[Throw Database Error]

    ThrowNotFound --> WrapperCatch[Wrapper Catches]
    ThrowDB --> WrapperCatch

    Handler -->|Validation Error| ZodError[Zod Validation Error]
    ZodError --> WrapperCatch

    WrapperCatch -->|ApiError| MapStatus[Map to HTTP status code]
    WrapperCatch -->|ZodError| Return422[Return 422]
    WrapperCatch -->|Unknown| Return500[Return 500]

    MapStatus --> Return404[Return 404/409/400]

    ReturnData --> Return200[Return 200 OK]

    Return200 --> Client[Client receives response]
    Return404 --> Client
    Return422 --> Client
    Return500 --> Client
```

---

## Database RPC Function Call Pattern

```mermaid
sequenceDiagram
    participant S as Service
    participant R as Repository
    participant C as Supabase Client
    participant DB as PostgreSQL Database
    participant RPC as RPC Function

    S->>R: Request data (e.g., getAllPlayersWithStats)
    R->>C: supabase.rpc('get_all_players_with_stats_optimized')
    C->>DB: Execute RPC function

    DB->>RPC: Call stored procedure
    RPC->>RPC: Execute CTE query<br/>Aggregate stats in SQL
    RPC->>DB: Return JSONB result

    DB->>C: Return result set
    C->>R: Return data
    R->>R: Map to TypeScript type
    R->>S: Return typed data

    Note over RPC: Single query replaces<br/>N+1 queries (41x faster)
```

---

## Summary

These class diagrams illustrate:

1. **System-Wide Architecture**: How frontend, backend, service, repository, and database layers interact
2. **Service Layer**: Pure ELO calculations and business logic orchestration
3. **Repository Layer**: Data access abstraction with Supabase client
4. **Domain Model**: Entity relationships in the database
5. **Type System**: TypeScript types and schemas used throughout
6. **Component Hierarchy**: React component composition
7. **API Routes**: Route handler structure and dependencies
8. **Match Creation**: Complete sequence from UI to database
9. **Rankings Display**: Data flow for player rankings with SWR caching
10. **ELO Calculation**: Step-by-step ELO computation with pool correction
11. **Props Flow**: How data flows between components
12. **Error Handling**: Error propagation and HTTP status mapping
13. **RPC Calls**: Optimized database query pattern

---

**Key Architectural Insights**:

- **Separation of Concerns**: Each layer has a single, well-defined responsibility
- **Dependency Inversion**: Services depend on repository abstractions, not Supabase directly
- **Type Safety**: TypeScript types flow from database to UI
- **Performance**: RPC functions optimize queries; SWR caches API responses
- **Error Handling**: Centralized error handling with domain-specific exceptions
- **Testability**: Pure functions (ELO service) and mockable repositories enable comprehensive testing

---

**Related Documentation**:
- [Architecture Overview](./01-architecture-overview.md)
- [Service Layer Reference](./05-service-layer.md)
- [Repository Layer Reference](./06-repository-layer.md)
- [Database Schema](./02-database-schema.md)
- [Sequence Diagrams](./03-sequence-diagrams.md)

**Last Updated**: 2025-12-26
