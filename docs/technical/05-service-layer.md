# Service Layer Documentation

**Last Updated**: 2025-12-26
**Document Type**: Class Reference
**Target Audience**: Backend Developers

---

## Overview

The service layer orchestrates business logic, coordinates repository calls, applies validation rules, and implements domain-specific workflows. Services are the **single source of truth for business rules** in the Baby Foot ELO system.

### Location
```text
lib/services/
├── elo.ts          # ELO calculation engine
├── matches.ts      # Match orchestration and ELO application
├── players.ts      # Player lifecycle and statistics
└── teams.ts        # Team lifecycle and statistics
```

### Design Pattern: Service Orchestration

Services follow a consistent pattern:
1. **Validate** input data (business rules, not just types)
2. **Fetch** required data via repositories
3. **Apply** business logic (calculations, transformations)
4. **Persist** changes via repositories
5. **Return** structured responses

**Key Rule**: Services **never** access the database directly. All database access goes through repositories.

---

## ELO Service (`lib/services/elo.ts`)

**Purpose**: Pure calculation engine for ELO rating changes with pool correction.

**Location**: `lib/services/elo.ts`
**Dependencies**: None (pure functions)
**Exports**: 10 functions

### Class Constants

```typescript
const K_TIER1 = 200  // ELO < 1200 (fast progression)
const K_TIER2 = 100  // 1200 <= ELO < 1800 (intermediate)
const K_TIER3 = 50   // ELO >= 1800 (stable, expert)
```

**Design Note**: K-factors are hardcoded constants (not configurable) to match the Python implementation exactly.

---

### Core Functions

#### `determineKFactor(currentElo: number): number`

**Purpose**: Determine K-factor based on current ELO tier.

**Parameters**:
- `currentElo` (number): Current ELO rating

**Returns**: `number` - K-factor (200, 100, or 50)

**Algorithm**:
```typescript
if (currentElo < 1200) return 200    // Tier 1: Beginners progress quickly
if (currentElo < 1800) return 100    // Tier 2: Intermediate stability
return 50                             // Tier 3: Experts change slowly
```

**Example**:
```typescript
determineKFactor(1050)  // → 200 (fast progression)
determineKFactor(1500)  // → 100 (moderate)
determineKFactor(2000)  // → 50 (stable)
```

**Location**: `lib/services/elo.ts:23-28`

---

#### `calculateTeamElo(player1Elo: number, player2Elo: number): number`

**Purpose**: Calculate team ELO as the average of two players' ELOs.

**Parameters**:
- `player1Elo` (number): First player's current ELO
- `player2Elo` (number): Second player's current ELO

**Returns**: `number` - Team ELO (truncated to integer)

**Formula**:
```text
Team ELO = Math.trunc((Player1 ELO + Player2 ELO) / 2)
```

**Note**: Uses `Math.trunc()` (not `Math.round()`) to match Python's integer division behavior.

**Example**:
```typescript
calculateTeamElo(1600, 1400)  // → 1500
calculateTeamElo(1650, 1550)  // → 1600
calculateTeamElo(1601, 1599)  // → 1600 (truncated, not rounded)
```

**Location**: `lib/services/elo.ts:55-63`

---

#### `calculateWinProbability(eloA: number, eloB: number): number`

**Purpose**: Calculate the probability that entity A wins against entity B using the standard ELO formula.

**Parameters**:
- `eloA` (number): ELO of entity A (player or team)
- `eloB` (number): ELO of entity B

**Returns**: `number` - Probability between 0 and 1

**Formula**:
```text
P(A wins) = 1 / (1 + 10^((ELO_B - ELO_A) / 400))
```

**Probability Table** (common scenarios):

| ELO_A | ELO_B | Difference | P(A wins) | Interpretation |
|-------|-------|------------|-----------|----------------|
| 1500  | 1500  | 0          | 0.50      | Even match |
| 1600  | 1500  | +100       | 0.64      | A favored |
| 1700  | 1500  | +200       | 0.76      | A heavily favored |
| 1400  | 1500  | -100       | 0.36      | B favored |

**Example**:
```typescript
calculateWinProbability(1600, 1400)  // → 0.7597 (76% chance A wins)
calculateWinProbability(1000, 2000)  // → 0.0001 (0.01% chance A wins)
```

**Location**: `lib/services/elo.ts:74-84`

---

#### `calculateEloChange(currentElo: number, expectedScore: number, actualScore: number): number`

**Purpose**: Calculate ELO change for a single entity based on expected vs actual performance.

**Parameters**:
- `currentElo` (number): Current ELO rating
- `expectedScore` (number): Expected score (0 to 1, from win probability)
- `actualScore` (number): Actual score (1 for win, 0 for loss)

**Returns**: `number` - ELO change (can be negative)

**Formula**:
```text
K = determineKFactor(currentElo)
ELO Change = K * (actualScore - expectedScore)
```

**Example**:
```typescript
// Player with 1600 ELO expected to win 76%, but lost
const expected = 0.76
const actual = 0  // Loss
const currentElo = 1600

calculateEloChange(currentElo, expected, actual)
// → -76 (loses more because loss was unexpected)

// Same player wins as expected
calculateEloChange(currentElo, 0.76, 1)
// → +24 (gains less because win was expected)
```

**Location**: `lib/services/elo.ts:126-140`

---

#### `calculateEloChangesWithPoolCorrection(changes: EloChangeInput[]): Map<string | number, number>`

**Purpose**: Apply pool correction to ensure zero-sum ELO changes across all entities.

**Parameters**:
- `changes` (EloChangeInput[]): Array of change objects
  ```typescript
  {
    id: string | number,
    initialChange: number,
    kFactor: number
  }
  ```

**Returns**: `Map<id, finalChange>` - Corrected ELO changes (guaranteed to sum to ~0)

**Algorithm**:
```text
1. Sum all initial changes
2. If sum ≈ 0, return initial changes (no correction needed)
3. Otherwise:
   a. Calculate total K-factor across all entities
   b. Correction = -sumOfChanges / totalKFactor
   c. For each entity:
      adjustedChange = initialChange + (kFactor * correction)
4. Return adjusted changes (now sum to 0)
```

**Why This Matters**: Prevents ELO inflation. Without correction, the total ELO in the system can grow over time due to rounding errors.

**Example**:
```typescript
const changes = [
  { id: 1, initialChange: 25, kFactor: 100 },
  { id: 2, initialChange: 25, kFactor: 100 },
  { id: 3, initialChange: -24, kFactor: 100 },
  { id: 4, initialChange: -24, kFactor: 100 }
]
// Sum = 2 (not zero-sum!)

const corrected = calculateEloChangesWithPoolCorrection(changes)
// → Map {
//   1 => 24.5,
//   2 => 24.5,
//   3 => -24.5,
//   4 => -24.5
// }
// Sum = 0 ✓
```

**Location**: `lib/services/elo.ts:152-191`

---

#### `calculatePlayersEloChange(winnerTeam: { players: Player[] }, loserTeam: { players: Player[] }): { playerChanges: Map<number, EloChange> }`

**Purpose**: Calculate ELO changes for all 4 players in a match with pool correction.

**Parameters**:
- `winnerTeam` (object): Team that won
  - `players` (Player[]): Array of 2 players with `player_id`, `global_elo`
- `loserTeam` (object): Team that lost
  - `players` (Player[]): Array of 2 players

**Returns**: Object with `playerChanges` Map
```typescript
{
  playerChanges: Map<playerId, {
    old_elo: number,
    new_elo: number,
    difference: number
  }>
}
```

**Process**:
1. Calculate team ELOs (average of players)
2. Calculate win probabilities
3. For each player:
   - Determine K-factor based on current ELO
   - Calculate initial ELO change
4. Apply pool correction (ensures zero-sum)
5. Return ELO changes for all 4 players

**Example**:
```typescript
const winnerTeam = {
  players: [
    { player_id: 1, global_elo: 1600 },
    { player_id: 2, global_elo: 1400 }
  ]
}
const loserTeam = {
  players: [
    { player_id: 3, global_elo: 1200 },
    { player_id: 4, global_elo: 1100 }
  ]
}

const result = calculatePlayersEloChange(winnerTeam, loserTeam)
// → {
//   playerChanges: Map {
//     1 => { old_elo: 1600, new_elo: 1624, difference: 24 },
//     2 => { old_elo: 1400, new_elo: 1424, difference: 24 },
//     3 => { old_elo: 1200, new_elo: 1184, difference: -16 },
//     4 => { old_elo: 1100, new_elo: 1067, difference: -33 }
//   }
// }
```

**Key Insight**: Players on the same team can have **different ELO changes** because they have different K-factors. This is the "hybrid" aspect of the hybrid ELO system.

**Location**: `lib/services/elo.ts:203-247`

---

#### `calculateTeamEloChange(winnerTeam: Team, loserTeam: Team): { teamChanges: Map<number, EloChange> }`

**Purpose**: Calculate ELO changes for both teams.

**Parameters**:
- `winnerTeam` (Team): Team that won (must have `team_id`, `global_elo`)
- `loserTeam` (Team): Team that lost

**Returns**: Object with `teamChanges` Map
```typescript
{
  teamChanges: Map<teamId, {
    old_elo: number,
    new_elo: number,
    difference: number
  }>
}
```

**Process**:
1. Calculate win probability based on team ELOs
2. For each team:
   - Determine K-factor based on current team ELO
   - Calculate initial ELO change
3. Apply pool correction
4. Return team ELO changes

**Example**:
```typescript
const winnerTeam = { team_id: 5, global_elo: 1500 }
const loserTeam = { team_id: 3, global_elo: 1150 }

const result = calculateTeamEloChange(winnerTeam, loserTeam)
// → {
//   teamChanges: Map {
//     5 => { old_elo: 1500, new_elo: 1530, difference: 30 },
//     3 => { old_elo: 1150, new_elo: 1120, difference: -30 }
//   }
// }
```

**Location**: `lib/services/elo.ts:257-303`

---

#### `processMatchResult(winnerTeam: FullTeam, loserTeam: FullTeam): ProcessedMatchResult`

**Purpose**: Orchestrate all ELO calculations for a match (both players and teams).

**Parameters**:
- `winnerTeam` (FullTeam): Winner with nested players
  ```typescript
  {
    team_id: number,
    global_elo: number,
    players: Player[]
  }
  ```
- `loserTeam` (FullTeam): Loser with nested players

**Returns**: `ProcessedMatchResult`
```typescript
{
  playerChanges: Map<playerId, EloChange>,
  teamChanges: Map<teamId, EloChange>
}
```

**Workflow**:
```text
1. Calculate player ELO changes (4 players)
   ├─ Team ELO calculation
   ├─ Win probability
   ├─ Individual K-factors
   └─ Pool correction
2. Calculate team ELO changes (2 teams)
   ├─ Win probability
   ├─ Team K-factors
   └─ Pool correction
3. Return both maps
```

**Example Usage** (from matches service):
```typescript
const result = processMatchResult(winnerTeamData, loserTeamData)

// Update player ELOs
for (const [playerId, change] of result.playerChanges) {
  await updatePlayerElo(playerId, change.new_elo)
}

// Update team ELOs
for (const [teamId, change] of result.teamChanges) {
  await updateTeamElo(teamId, change.new_elo)
}
```

**Location**: `lib/services/elo.ts:315-338`

---

## Match Service (`lib/services/matches.ts`)

**Purpose**: Orchestrate match creation, ELO application, and match queries.

**Location**: `lib/services/matches.ts`
**Dependencies**:
- Match Repository
- Team Service
- ELO Service
- Player/Team Repositories (for ELO updates)

**Exports**: 8 functions

---

### Core Functions

#### `createNewMatch(data: MatchCreate): Promise<MatchWithEloResponse>`

**Purpose**: Create a match, calculate ELO changes, update all entities, record history.

**Parameters**:
- `data` (MatchCreate):
  ```typescript
  {
    winner_team_id: number,
    loser_team_id: number,
    is_fanny: boolean,
    played_at: string,  // ISO date
    notes?: string
  }
  ```

**Returns**: `Promise<MatchWithEloResponse>` - Match with ELO changes

**Workflow** (9 steps):

```bash
1. Validate teams are different
   ├─ Throws InvalidMatchTeamsError if same team

2. Fetch winner team with players
   ├─ Uses getTeam(winner_team_id)
   └─ Throws TeamNotFoundError if missing

3. Fetch loser team with players
   ├─ Uses getTeam(loser_team_id)
   └─ Throws TeamNotFoundError if missing

4. Create match record in database
   ├─ Calls createMatchByTeamIds()
   └─ Returns match_id

5. Calculate ELO changes
   ├─ Calls processMatchResult()
   └─ Returns playerChanges + teamChanges Maps

6. Batch update player ELOs
   ├─ Convert Map to update array
   ├─ Calls batchUpdatePlayersElo()
   └─ Sequential updates (4 players)

7. Record player ELO history
   ├─ For each player change
   ├─ Calls recordPlayerEloHistory()
   └─ Stores in players_elo_history table

8. Batch update team ELOs
   ├─ Convert Map to update array
   ├─ Calls batchUpdateTeamsElo()
   └─ Sequential updates (2 teams)

9. Record team ELO history
   ├─ For each team change
   ├─ Calls recordTeamEloHistory()
   └─ Stores in teams_elo_history table

Return: MatchWithEloResponse
```

**Example**:
```typescript
const matchData = {
  winner_team_id: 5,
  loser_team_id: 3,
  is_fanny: false,
  played_at: new Date().toISOString(),
  notes: 'Championship final'
}

const result = await createNewMatch(matchData)
// → {
//   match_id: 42,
//   winner_team_id: 5,
//   loser_team_id: 3,
//   is_fanny: false,
//   played_at: '2025-12-26T...',
//   notes: 'Championship final',
//   elo_changes: {
//     '1': { old_elo: 1600, new_elo: 1624, difference: 24 },
//     '2': { old_elo: 1400, new_elo: 1424, difference: 24 },
//     '3': { old_elo: 1200, new_elo: 1184, difference: -16 },
//     '4': { old_elo: 1100, new_elo: 1067, difference: -33 }
//   }
// }
```

**Location**: `lib/services/matches.ts:158-303`

**Critical Notes**:
- **Transaction**: Not wrapped in a database transaction. If any step fails midway, partial updates may occur. This matches the Python implementation behavior.
- **ELO History**: Always recorded even if match is later deleted.
- **Zero-Sum**: Pool correction ensures sum of all player ELO changes ≈ 0.

---

#### `getMatch(matchId: number): Promise<MatchResponse>`

**Purpose**: Retrieve a single match by ID.

**Parameters**:
- `matchId` (number): Match identifier

**Returns**: `Promise<MatchResponse>` - Match data

**Throws**: `MatchNotFoundError` if match doesn't exist

**Example**:
```typescript
const match = await getMatch(42)
// → {
//   match_id: 42,
//   winner_team_id: 5,
//   loser_team_id: 3,
//   is_fanny: false,
//   played_at: '2025-12-26T19:30:00Z',
//   notes: 'Championship final'
// }
```

**Location**: `lib/services/matches.ts:56-63`

---

#### `getMatches(options?: { start_date?: string, end_date?: string, is_fanny?: boolean }): Promise<MatchResponse[]>`

**Purpose**: Get all matches with optional filtering.

**Parameters**:
- `options` (optional):
  - `start_date` (string, optional): ISO date, filter matches after this date
  - `end_date` (string, optional): ISO date, filter matches before this date
  - `is_fanny` (boolean, optional): Filter for fanny matches only

**Returns**: `Promise<MatchResponse[]>` - Array of matches

**Example**:
```typescript
// All matches
const allMatches = await getMatches()

// Matches in December 2025
const decemberMatches = await getMatches({
  start_date: '2025-12-01',
  end_date: '2025-12-31'
})

// All fanny matches
const fannyMatches = await getMatches({ is_fanny: true })
```

**Location**: `lib/services/matches.ts:72-85`

---

#### `getMatchesByPlayer(playerId: number, options?: PaginationOptions): Promise<{ matches: any[], total: number }>`

**Purpose**: Get match history for a specific player with pagination.

**Parameters**:
- `playerId` (number): Player identifier
- `options` (PaginationOptions, optional):
  ```typescript
  {
    limit?: number,   // Default: 50
    offset?: number   // Default: 0
  }
  ```

**Returns**: Promise resolving to:
```typescript
{
  matches: MatchWithEloChange[],  // Includes ELO changes for this player
  total: number                   // Total count (for pagination)
}
```

**Special Feature**: Each match includes the ELO change for this specific player.

**Example**:
```typescript
const result = await getMatchesByPlayer(1, { limit: 10, offset: 0 })
// → {
//   matches: [
//     {
//       match_id: 42,
//       team_id: 5,
//       is_winner: true,
//       opponent_team_id: 3,
//       elo_change: 24,  // ← This player's ELO change
//       played_at: '2025-12-26T...',
//       ...
//     },
//     ...
//   ],
//   total: 156
// }
```

**Location**: `lib/services/matches.ts:94-119`

---

#### `getMatchesWithTeamElo(teamId: number): Promise<TeamMatchHistory[]>`

**Purpose**: Get match history for a team with team-level ELO changes.

**Parameters**:
- `teamId` (number): Team identifier

**Returns**: `Promise<TeamMatchHistory[]>` - Array of matches with team ELO data

**Example**:
```typescript
const history = await getMatchesWithTeamElo(5)
// → [
//   {
//     match_id: 42,
//     winner_team_id: 5,
//     loser_team_id: 3,
//     is_winner: true,
//     team_elo_change: 30,  // ← Team's ELO change
//     played_at: '2025-12-26T...',
//     ...
//   },
//   ...
// ]
```

**Location**: `lib/services/matches.ts:128-149`

---

#### `deleteMatch(matchId: number): Promise<void>`

**Purpose**: Delete a match record.

**Parameters**:
- `matchId` (number): Match to delete

**Returns**: `Promise<void>`

**Throws**: `MatchNotFoundError` if match doesn't exist

**⚠️ CRITICAL WARNING**:
```typescript
// [!]: Does not reverse ELO changes (matches Python implementation behavior)
```

When you delete a match:
- ✓ Match record is removed
- ✗ Player ELOs are **NOT** reverted
- ✗ Team ELOs are **NOT** reverted
- ✗ ELO history records remain

This is **intentional** to match the original Python backend behavior.

**Example**:
```typescript
await deleteMatch(42)
// Match removed, but ELO changes from that match remain permanent
```

**Location**: `lib/services/matches.ts:389-395`

---

## Player Service (`lib/services/players.ts`)

**Purpose**: Manage player lifecycle, statistics, and auto-team creation.

**Location**: `lib/services/players.ts`
**Dependencies**:
- Player Repository
- Team Repository
- Stats Repository
- ELO History Repository

**Exports**: 7 functions

---

### Core Functions

#### `createNewPlayer(data: PlayerCreate): Promise<PlayerResponse>`

**Purpose**: Create a new player and automatically create teams with all existing players.

**Parameters**:
- `data` (PlayerCreate):
  ```typescript
  {
    name: string,
    global_elo?: number  // Optional, defaults to 1000
  }
  ```

**Returns**: `Promise<PlayerResponse>` - Created player

**Throws**:
- `PlayerAlreadyExistsError` if name already exists

**Special Behavior**: **Auto-Team Creation**

When a new player is created:
1. Player record is inserted
2. All existing players are fetched
3. For each existing player:
   - Create a team pairing new player with existing player
   - Team ELO defaults to 1000

**Why?** This enables the new player to immediately participate in matches without manually creating teams first.

**Example**:
```typescript
// Existing players: Alice (id=1), Bob (id=2)

const charlie = await createNewPlayer({ name: 'Charlie' })
// → Player created with id=3

// Teams automatically created:
// - Team(1,3): Alice & Charlie
// - Team(2,3): Bob & Charlie
```

**Location**: `lib/services/players.ts:23-74`

**Performance Note**: If you have 100 existing players, creating a new player creates 100 teams. This is acceptable since player registration is infrequent.

---

#### `getAllPlayersWithStats(limit?: number): Promise<PlayerResponse[]>`

**Purpose**: Get all players with computed statistics (matches, wins, losses, win rate).

**Parameters**:
- `limit` (number, optional): Max players to return (default: unlimited)

**Returns**: `Promise<PlayerResponse[]>` - Players sorted by ELO descending

**Data Includes**:
- Basic: `player_id`, `name`, `global_elo`
- Stats: `matches_played`, `wins`, `losses`, `win_rate`
- Metadata: `rank` (1-indexed), `last_match_at`

**Example**:
```typescript
const rankings = await getAllPlayersWithStats(10)  // Top 10
// → [
//   {
//     player_id: 5,
//     name: 'Alice',
//     global_elo: 1850,
//     rank: 1,
//     matches_played: 120,
//     wins: 85,
//     losses: 35,
//     win_rate: 0.708,
//     last_match_at: '2025-12-26T...'
//   },
//   ...
// ]
```

**Location**: `lib/services/players.ts:83-96`

**Optimization**: Uses RPC function `get_all_players_with_stats_optimized` which is 41x faster than the helper-function approach.

---

#### `getPlayer(playerId: number): Promise<PlayerResponse>`

**Purpose**: Get a single player by ID with full statistics.

**Parameters**:
- `playerId` (number): Player identifier

**Returns**: `Promise<PlayerResponse>` - Player with stats

**Throws**: `PlayerNotFoundError` if player doesn't exist

**Example**:
```typescript
const player = await getPlayer(5)
// → {
//   player_id: 5,
//   name: 'Alice',
//   global_elo: 1850,
//   matches_played: 120,
//   wins: 85,
//   losses: 35,
//   win_rate: 0.708,
//   last_match_at: '2025-12-26T...'
// }
```

**Location**: `lib/services/players.ts:105-125`

---

#### `updateExistingPlayer(playerId: number, data: PlayerUpdate): Promise<PlayerResponse>`

**Purpose**: Update a player's name or ELO.

**Parameters**:
- `playerId` (number): Player to update
- `data` (PlayerUpdate):
  ```typescript
  {
    name?: string,
    global_elo?: number
  }
  ```

**Returns**: `Promise<PlayerResponse>` - Updated player

**Throws**:
- `PlayerNotFoundError` if player doesn't exist
- `PlayerAlreadyExistsError` if new name conflicts

**Validation**:
- If updating name: checks for uniqueness
- At least one field must be provided

**Example**:
```typescript
// Rename player
await updateExistingPlayer(5, { name: 'Alice Johnson' })

// Adjust ELO manually (rare)
await updateExistingPlayer(5, { global_elo: 1900 })
```

**Location**: `lib/services/players.ts:134-166`

**⚠️ Warning**: Manually updating `global_elo` breaks the integrity of the ELO system. This should only be done for admin corrections.

---

#### `deletePlayer(playerId: number): Promise<void>`

**Purpose**: Delete a player.

**Parameters**:
- `playerId` (number): Player to delete

**Returns**: `Promise<void>`

**Throws**: `PlayerNotFoundError` if player doesn't exist

**Cascade Behavior**:
- Database foreign key constraints handle cascading deletes
- Teams containing this player are deleted
- Match records remain but may reference non-existent teams

**Example**:
```typescript
await deletePlayer(5)
// Player removed
// All teams with player_id=5 also removed
```

**Location**: `lib/services/players.ts:175-181`

---

#### `getPlayerEloHistory(playerId: number): Promise<EloHistoryResponse[]>`

**Purpose**: Get ELO change history for a player.

**Parameters**:
- `playerId` (number): Player identifier

**Returns**: `Promise<EloHistoryResponse[]>` - Array of ELO changes

**Data Structure**:
```typescript
{
  history_id: number,
  player_id: number,
  match_id: number,
  old_elo: number,
  new_elo: number,
  difference: number,
  date: string
}
```

**Example**:
```typescript
const history = await getPlayerEloHistory(5)
// → [
//   {
//     history_id: 1,
//     player_id: 5,
//     match_id: 42,
//     old_elo: 1850,
//     new_elo: 1874,
//     difference: 24,
//     date: '2025-12-26T...'
//   },
//   ...
// ]
```

**Location**: `lib/services/players.ts:190-197`

**Use Case**: Display ELO progression chart on player detail page.

---

## Team Service (`lib/services/teams.ts`)

**Purpose**: Manage team lifecycle, normalization, and active team rankings.

**Location**: `lib/services/teams.ts`
**Dependencies**:
- Team Repository
- Player Repository
- Stats Repository

**Exports**: 7 functions

---

### Core Functions

#### `createNewTeam(data: TeamCreate): Promise<TeamResponse>`

**Purpose**: Create a new team from two players.

**Parameters**:
- `data` (TeamCreate):
  ```typescript
  {
    player1_id: number,
    player2_id: number,
    global_elo?: number  // Optional, defaults to 1000
  }
  ```

**Returns**: `Promise<TeamResponse>` - Created team

**Throws**:
- `PlayerNotFoundError` if either player doesn't exist
- Error if team already exists (handled by unique constraint)

**Key Behavior**: **Player ID Normalization**

Player IDs are automatically sorted so that:
```typescript
createNewTeam({ player1_id: 5, player2_id: 3 })
// Stored as: player1_id=3, player2_id=5 (min first)
```

This ensures `Team(3,5)` and `Team(5,3)` are treated as the same team.

**Example**:
```typescript
const team = await createNewTeam({
  player1_id: 3,
  player2_id: 5
})
// → {
//   team_id: 10,
//   player1_id: 3,  // Always lower ID
//   player2_id: 5,  // Always higher ID
//   global_elo: 1000,
//   created_at: '2025-12-26T...'
// }
```

**Location**: `lib/services/teams.ts:47-78`

---

#### `getAllTeamsWithStats(limit?: number): Promise<TeamResponse[]>`

**Purpose**: Get all teams with computed statistics.

**Parameters**:
- `limit` (number, optional): Max teams to return

**Returns**: `Promise<TeamResponse[]>` - Teams sorted by ELO descending

**Data Includes**:
- Basic: `team_id`, `player1_id`, `player2_id`, `global_elo`
- Stats: `matches_played`, `wins`, `losses`, `win_rate`
- Metadata: `rank`, `last_match_at`

**Example**:
```typescript
const teams = await getAllTeamsWithStats(10)  // Top 10
// → [
//   {
//     team_id: 10,
//     player1_id: 3,
//     player2_id: 5,
//     global_elo: 1750,
//     rank: 1,
//     matches_played: 45,
//     wins: 30,
//     losses: 15,
//     win_rate: 0.667,
//     last_match_at: '2025-12-26T...'
//   },
//   ...
// ]
```

**Location**: `lib/services/teams.ts:87-100`

---

#### `getActiveTeamRankings(limit?: number): Promise<TeamResponse[]>`

**Purpose**: Get **active** team rankings (teams with significant recent activity).

**Parameters**:
- `limit` (number, optional): Max teams to return

**Returns**: `Promise<TeamResponse[]>` - Active teams only

**Active Team Definition**:
```bash
A team is active if:
- Has played >= 10 matches, AND
- Last match was within the last 180 days
```

**Why?** Prevents "ghost" teams (created long ago, never played) from cluttering rankings.

**Example**:
```typescript
const activeTeams = await getActiveTeamRankings(20)
// Only returns teams that:
// - Have 10+ matches
// - Played in the last 6 months
```

**Location**: `lib/services/teams.ts:109-122`

**Use Case**: Display on homepage or leaderboard to show only relevant teams.

---

#### `getTeam(teamId: number): Promise<TeamResponse>`

**Purpose**: Get a single team by ID with full statistics.

**Parameters**:
- `teamId` (number): Team identifier

**Returns**: `Promise<TeamResponse>` - Team with stats

**Throws**: `TeamNotFoundError` if team doesn't exist

**Example**:
```typescript
const team = await getTeam(10)
// → {
//   team_id: 10,
//   player1_id: 3,
//   player2_id: 5,
//   global_elo: 1750,
//   matches_played: 45,
//   wins: 30,
//   losses: 15,
//   win_rate: 0.667,
//   last_match_at: '2025-12-26T...',
//   created_at: '2025-01-15T...'
// }
```

**Location**: `lib/services/teams.ts:131-151`

---

#### `getTeamsByPlayer(playerId: number): Promise<TeamResponse[]>`

**Purpose**: Get all teams that include a specific player.

**Parameters**:
- `playerId` (number): Player identifier

**Returns**: `Promise<TeamResponse[]>` - All teams containing this player

**Example**:
```typescript
const teams = await getTeamsByPlayer(3)
// → [
//   { team_id: 10, player1_id: 3, player2_id: 5, ... },
//   { team_id: 11, player1_id: 2, player2_id: 3, ... },
//   { team_id: 12, player1_id: 3, player2_id: 7, ... }
// ]
```

**Location**: `lib/services/teams.ts:160-173`

**Use Case**: Show all partnerships on player detail page.

---

#### `updateExistingTeam(teamId: number, data: TeamUpdate): Promise<TeamResponse>`

**Purpose**: Update a team's ELO or last match timestamp.

**Parameters**:
- `teamId` (number): Team to update
- `data` (TeamUpdate):
  ```typescript
  {
    global_elo?: number,
    last_match_at?: string  // ISO timestamp
  }
  ```

**Returns**: `Promise<TeamResponse>` - Updated team

**Throws**: `TeamNotFoundError` if team doesn't exist

**Example**:
```typescript
// Update team ELO manually (rare)
await updateExistingTeam(10, { global_elo: 1800 })

// Update last match timestamp
await updateExistingTeam(10, {
  last_match_at: new Date().toISOString()
})
```

**Location**: `lib/services/teams.ts:182-204`

**⚠️ Warning**: Manually updating `global_elo` breaks ELO integrity. Should only be used for admin corrections.

---

#### `deleteTeam(teamId: number): Promise<void>`

**Purpose**: Delete a team.

**Parameters**:
- `teamId` (number): Team to delete

**Returns**: `Promise<void>`

**Throws**: `TeamNotFoundError` if team doesn't exist

**Example**:
```typescript
await deleteTeam(10)
// Team removed from database
```

**Location**: `lib/services/teams.ts:213-219`

---

## Service Layer Design Principles

### 1. Single Responsibility
Each service manages **one domain entity**:
- `elo.ts`: Pure ELO calculations
- `matches.ts`: Match orchestration
- `players.ts`: Player lifecycle
- `teams.ts`: Team lifecycle

### 2. Repository Abstraction
Services **never** access the database directly. All database operations go through repositories.

```typescript
// ❌ BAD: Service accessing Supabase directly
const { data } = await supabase.from('players').select('*')

// ✅ GOOD: Service using repository
const players = await getAllPlayers()
```

### 3. Error Handling
Services throw **domain-specific errors** (not generic exceptions):

```typescript
// ❌ BAD: Generic error
throw new Error('Player not found')

// ✅ GOOD: Domain error
throw new PlayerNotFoundError(playerId)
```

### 4. Validation
Services validate **business rules**, not just types:

```typescript
// Type validation (Zod) happens at API route level
// Business validation happens at service level

if (winnerTeamId === loserTeamId) {
  throw new InvalidMatchTeamsError('Teams must be different')
}
```

### 5. Pure Functions (ELO Service)
ELO calculation functions are **pure** (no side effects, no database access). This makes them:
- Easy to test
- Easy to reason about
- Reusable across contexts

### 6. Transaction-Free (By Design)
Services do **not** use database transactions. This matches the original Python implementation.

**Trade-off**:
- ❌ Risk of partial updates on failure
- ✅ Simpler code, easier to understand
- ✅ Works fine for low-frequency operations (match creation)

---

## Testing Services

### Unit Testing (ELO Service)

```typescript
import { calculateTeamElo, determineKFactor } from '@/lib/services/elo'

describe('ELO Service', () => {
  test('calculateTeamElo averages player ELOs', () => {
    expect(calculateTeamElo(1600, 1400)).toBe(1500)
  })

  test('determineKFactor returns correct tier', () => {
    expect(determineKFactor(1050)).toBe(200)
    expect(determineKFactor(1500)).toBe(100)
    expect(determineKFactor(2000)).toBe(50)
  })
})
```

### Integration Testing (Other Services)

```typescript
import { createNewMatch } from '@/lib/services/matches'

describe('Match Service', () => {
  test('createNewMatch updates player ELOs', async () => {
    // Arrange: Create players and teams
    // Act: Create match
    const result = await createNewMatch(matchData)

    // Assert: Verify ELO changes
    expect(result.elo_changes['1'].difference).toBeGreaterThan(0)
  })
})
```

---

## Common Patterns

### Fetching with Error Handling

```typescript
const player = await getPlayerById(playerId)
if (!player) {
  throw new PlayerNotFoundError(playerId)
}
```

### Batch Updates

```typescript
const updates = Array.from(playerChanges.entries()).map(([id, change]) => ({
  player_id: id,
  global_elo: change.new_elo
}))
await batchUpdatePlayersElo(updates)
```

### Mapping Repository Data to Response

```typescript
const playerRow = await getPlayerWithStats(playerId)
return mapPlayerWithStatsToResponse(playerRow)  // Mapper function
```

---

## Maintenance Notes

### When Adding New Features

1. **Identify Domain**: Does this belong in player, team, match, or ELO service?
2. **Check Repository**: Do you need new repository functions?
3. **Validate Business Rules**: Add validation in service (not just API)
4. **Update Types**: Add new types to `types/` and schemas to `lib/types/schemas/`
5. **Test**: Write integration tests for new service functions

### When Modifying ELO Logic

**⚠️ CRITICAL**: ELO service is a direct port from Python. Changes must:
1. Maintain zero-sum property (pool correction)
2. Preserve K-factor tiers
3. Match Python implementation exactly
4. Be thoroughly tested with known examples

**Before modifying**:
1. Read `docs/technical/04-elo-calculation-system.md`
2. Understand pool correction algorithm
3. Add test cases that verify zero-sum property

---

## Summary

The service layer is the **heart of business logic** in Baby Foot ELO. It:
- Orchestrates complex workflows (match creation with ELO updates)
- Enforces business rules (team validation, player uniqueness)
- Coordinates multiple repositories
- Provides clean interfaces for API routes
- Contains the critical ELO calculation engine

**Key Takeaway**: Services are **stateless orchestrators**. They don't hold data; they coordinate repositories and apply domain logic.

---

**Next**: [Repository Layer Documentation](./06-repository-layer.md)

**Last Updated**: 2025-12-26
