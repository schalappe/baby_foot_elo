# Component Reference

**Document Type**: Technical Reference
**Target Audience**: Frontend developers
**Last Updated**: 2025-12-26
**Maintained By**: Development Team

---

## Table of Contents

1. [Overview](#overview)
2. [Layout Components](#layout-components)
3. [Common Components](#common-components)
4. [Player Components](#player-components)
5. [Team Components](#team-components)
6. [Match Components](#match-components)
7. [Rankings Components](#rankings-components)
8. [UI Primitives](#ui-primitives-shadcn)

---

## Overview

This document provides detailed documentation for all React components in the Baby Foot ELO application. Components are organized by domain (players, teams, matches, rankings) and layer (layout, common, domain-specific, UI primitives).

### Component Count

| Category | Count | Location |
|----------|-------|----------|
| Layout Components | 4 | `components/` |
| Common Components | 6 | `components/common/` |
| Player Components | 8 | `components/players/` |
| Team Components | 6 | `components/teams/` |
| Match Components | 3 | `components/matches/` |
| Rankings Components | 4 | `components/rankings/` |
| UI Primitives (ShadCN) | 43 | `components/ui/` |
| **Total** | **74** | |

---

## Layout Components

### AppSidebar

**Purpose**: Main navigation sidebar with collapsible sections

**File**: `components/app-sidebar.tsx`

**Props**: None (uses ShadCN Sidebar context)

**Features**:
- Championship trophy logo with title
- Collapsible sections: Rankings, Matches, Admin
- Theme toggle in footer
- Responsive (collapses on mobile)
- Icons from Lucide React

**Structure**:
```typescript
<Sidebar>
  <SidebarHeader>
    <Link href="/">
      <Trophy /> Baby Foot Championship
    </Link>
  </SidebarHeader>

  <SidebarContent>
    <SidebarGroup>
      <SidebarGroupLabel>Rankings</SidebarGroupLabel>
      <SidebarGroupContent>
        <SidebarMenuItem>
          <Link href="/">Players</Link>
        </SidebarMenuItem>
        <SidebarMenuItem>
          <Link href="/teams">Teams</Link>
        </SidebarMenuItem>
      </SidebarGroupContent>
    </SidebarGroup>

    <SidebarGroup>
      <SidebarGroupLabel>Matches</SidebarGroupLabel>
      <SidebarGroupContent>
        <SidebarMenuItem>
          <Link href="/matches/new">New Match</Link>
        </SidebarMenuItem>
        <SidebarMenuItem>
          <Link href="/matches">Match History</Link>
        </SidebarMenuItem>
      </SidebarGroupContent>
    </SidebarGroup>
  </SidebarContent>

  <SidebarFooter>
    <ThemeToggle />
  </SidebarFooter>
</Sidebar>
```

**Usage**:
```typescript
// app/layout.tsx
import { AppSidebar } from "@/components/app-sidebar";

export default function RootLayout({ children }) {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset>{children}</SidebarInset>
    </SidebarProvider>
  );
}
```

---

### Header

**Purpose**: Page header with breadcrumbs and sidebar toggle

**File**: `components/Header.tsx`

**Props**:
```typescript
interface HeaderProps {
  title?: string;           // Optional page title
  breadcrumbs?: Breadcrumb[]; // Optional breadcrumb trail
}

interface Breadcrumb {
  label: string;
  href?: string;
}
```

**Features**:
- Sidebar toggle button (mobile)
- Breadcrumb navigation
- Responsive design

**Usage**:
```typescript
<Header
  title="Player Rankings"
  breadcrumbs={[
    { label: "Home", href: "/" },
    { label: "Players" },
  ]}
/>
```

---

### ThemeProvider

**Purpose**: Dark mode context provider

**File**: `components/ThemeProvider.tsx`

**Props**:
```typescript
interface ThemeProviderProps {
  children: ReactNode;
  attribute?: string;        // Default: "class"
  defaultTheme?: string;     // Default: "system"
  enableSystem?: boolean;    // Default: true
}
```

**Features**:
- Wraps `next-themes` provider
- System theme detection
- Persists theme preference to localStorage

**Usage**:
```typescript
// app/layout.tsx
import { ThemeProvider } from "@/components/ThemeProvider";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
```

---

### ThemeToggle

**Purpose**: Toggle button for dark/light mode

**File**: `components/ThemeToggle.tsx`

**Props**: None

**Features**:
- Sun/Moon icon transition
- Smooth theme switching
- Tooltip with keyboard shortcut

**Usage**:
```typescript
<ThemeToggle />
```

**Implementation**:
```typescript
export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
    >
      <Sun className="h-5 w-5 rotate-0 scale-100 dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-5 w-5 rotate-90 scale-0 dark:rotate-0 dark:scale-100" />
    </Button>
  );
}
```

---

## Common Components

### EntityStatsCards

**Purpose**: Generic 3-card stats display (ELO hero, chart, winrate)

**File**: `components/common/EntityStatsCards.tsx`

**Props**:
```typescript
interface EntityStatsCardsProps {
  stats: EntityStats;
}

interface EntityStats {
  global_elo: number;
  elo_values: number[];      // Historical ELO values
  wins: number;
  losses: number;
  win_rate: number;          // 0-1 decimal
  recent: {
    elo_changes: number[];   // Last N match ELO changes
    win_rate: number;
    wins: number;
    losses: number;
  };
}
```

**Features**:
- **Card 1**: ELO hero card with trend badge
  - Current ELO (large number)
  - Recent ELO change badge (green +/red -)
  - Win/loss count

- **Card 2**: ELO evolution line chart (Recharts)
  - X-axis: Match number
  - Y-axis: ELO value
  - Gradient fill under line

- **Card 3**: Winrate donut chart (Recharts)
  - Pie chart with wins/losses
  - Center: Win rate percentage
  - Win-loss record summary

**Layout**:
```text
┌─────────────────────────────────────────────────┐
│  ┌─────────┐  ┌──────────────────────┐          │
│  │ 1650    │  │ ELO Evolution        │          │
│  │ +24     │  │ [Line Chart]         │          │
│  │ W-L     │  │                      │          │
│  └─────────┘  └──────────────────────┘          │
│                                                 │
│  ┌──────────────────────┐                       │
│  │ Winrate Donut        │                       │
│  │ [Pie Chart] 65%      │                       │
│  │ 25W - 17L            │                       │
│  └──────────────────────┘                       │
└─────────────────────────────────────────────────┘
```

**Used By**:
- `PlayerStatsCards` (wrapper)
- `TeamStatsCards` (wrapper)

**Usage**:
```typescript
<EntityStatsCards stats={playerStats} />
```

---

### EntityMatchesSection

**Purpose**: Paginated match history grouped by date

**File**: `components/common/EntityMatchesSection.tsx`

**Props**:
```typescript
interface EntityMatchesSectionProps {
  entityId: number;
  entityType: 'player' | 'team';
  matches: Match[];
  loading: boolean;
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

interface Match {
  match_id: number;
  winner_team_id: number;
  loser_team_id: number;
  winner_team?: Team;
  loser_team?: Team;
  is_fanny: boolean;
  played_at: string;         // ISO datetime
  notes?: string;
  player_elo_change?: number; // For player matches
  team_elo_change?: number;   // For team matches
}
```

**Features**:
- Groups matches by date (`YYYY-MM-DD`)
- Displays match cards with winner/loser teams
- Shows ELO change badges (green for gain, red for loss)
- Fanny indicator (skull icon)
- Pagination controls (previous/next, page numbers)
- Loading skeleton during fetch
- Empty state when no matches

**Layout**:
```text
┌─────────────────────────────────────────────┐
│  📅 2025-12-26 (3 matches)                  │
│                                             │
│  ┌──────────────────────────────────────┐   │
│  │ Match #101           [+24 ELO] ✅    │   │
│  │ Team A  vs  Team B                   │   │
│  │ 14:22                                │   │
│  └──────────────────────────────────────┘   │
│                                             │
│  ┌──────────────────────────────────────┐   │
│  │ Match #102           [-16 ELO] ❌    │   │
│  │ Team C  vs  Team D                   │   │
│  │ 15:30                                │   │
│  └──────────────────────────────────────┘   │
│                                             │
│  📅 2025-12-25 (2 matches)                  │
│  ...                                        │
│                                             │
│  ◀ 1 2 3 ▶  (Pagination)                    │
└─────────────────────────────────────────────┘
```

**Used By**:
- `PlayerMatchesSection` (wrapper)
- `TeamMatchesSection` (wrapper)

**Usage**:
```typescript
<EntityMatchesSection
  entityId={playerId}
  entityType="player"
  matches={matches}
  loading={matchesLoading}
  currentPage={currentPage}
  totalPages={totalPages}
  onPageChange={setCurrentPage}
/>
```

---

### RankingTable

**Purpose**: Generic sortable/filterable table using TanStack Table

**File**: `components/common/RankingTable.tsx`

**Props**:
```typescript
function RankingTable<T>({
  data: T[];
  columns: ColumnDef<T>[];
  isLoading: boolean;
  error: Error | null;
}): JSX.Element
```

**Features**:
- Client-side sorting (all columns)
- Client-side filtering (search)
- Client-side pagination
- 5 skeleton rows during loading
- Responsive design (horizontal scroll on mobile)
- Error state display
- Empty state when no data

**Column Definition Example**:
```typescript
const columns: ColumnDef<Player>[] = [
  {
    accessorKey: "rank",
    header: () => <div className="text-center">Rank</div>,
    cell: ({ row }) => (
      <div className="text-center font-bold">{row.getValue("rank")}</div>
    ),
  },
  {
    accessorKey: "name",
    header: ({ column }) => (
      <Button
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
      >
        Name
        <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    ),
    cell: ({ row }) => (
      <Link href={`/players/${row.original.player_id}`}>
        {row.getValue("name")}
      </Link>
    ),
  },
  {
    accessorKey: "global_elo",
    header: () => <div className="text-center">ELO</div>,
    cell: ({ row }) => (
      <div className="text-center font-mono">{row.getValue("global_elo")}</div>
    ),
  },
];
```

**Used By**:
- `PlayerRankingTable`
- `TeamRankingTable`

**Usage**:
```typescript
<RankingTable
  data={players}
  columns={playerColumns}
  isLoading={loading}
  error={error}
/>
```

---

### PodiumGrid

**Purpose**: Championship-styled top 3 display

**File**: `components/common/PodiumGrid.tsx`

**Props**:
```typescript
function PodiumGrid<T>({
  items: T[];                               // Top 3 items (length 1-3)
  getKey: (item: T, index: number) => React.Key;
  getLink: (item: T) => string;
  getName: (item: T) => ReactNode;
  getElo: (item: T) => ReactNode;
  getWinrate: (item: T) => ReactNode;
  renderExtra?: (item: T) => ReactNode;     // Optional extra content
}): JSX.Element
```

**Features**:
- Displays 1-3 items in podium layout
- Gold/Silver/Bronze card styling with gradients
- Trophy/Medal/Award icons (Lucide React)
- 3-card grid layout (responsive: stacked on mobile)
- Hover animations (scale-105)
- Click to navigate to detail page

**Layout**:
```text
Desktop (3-column grid):
┌──────────────────────────────────────────┐
│  🥈 #2        🥇 #1        🥉 #3         │
│  Silver       Gold         Bronze        │
│  Player 2     Player 1     Player 3      │
│  1580 ELO     1650 ELO     1520 ELO      │
│  72% WR       68% WR       65% WR        │
└──────────────────────────────────────────┘

Mobile (stacked):
┌────────────┐
│  🥇 #1     │
│  Gold      │
│  Player 1  │
│  1650 ELO  │
│  68% WR    │
├────────────┤
│  🥈 #2     │
│  ...       │
├────────────┤
│  🥉 #3     │
│  ...       │
└────────────┘
```

**Styling**:
```css
/* Gold Card */
bg-gradient-to-br from-yellow-400 to-yellow-600
shadow-2xl shadow-yellow-500/50

/* Silver Card */
bg-gradient-to-br from-gray-300 to-gray-500
shadow-2xl shadow-gray-400/50

/* Bronze Card */
bg-gradient-to-br from-amber-600 to-amber-800
shadow-2xl shadow-amber-700/50
```

**Used By**:
- `PlayerRankingsDisplay`
- `TeamRankingsDisplay`

**Usage**:
```typescript
<PodiumGrid
  items={topPlayers.slice(0, 3)}
  getKey={(player) => player.player_id}
  getLink={(player) => `/players/${player.player_id}`}
  getName={(player) => player.name}
  getElo={(player) => player.global_elo}
  getWinrate={(player) =>
    `${Math.round(player.win_rate * 100)}%`
  }
  renderExtra={(player) => (
    <div className="text-sm text-white/90">
      {player.wins}W - {player.losses}L
    </div>
  )}
/>
```

---

### EntityLoadingSkeleton

**Purpose**: Generic loading placeholder with skeleton UI

**File**: `components/common/EntityLoadingSkeleton.tsx`

**Props**: None

**Features**:
- Mimics layout of detail page
- Animated pulse effect
- 3 skeleton cards (stats cards)
- Skeleton match list

**Layout**:
```text
┌─────────────────────────────────────────┐
│  ████████ (Title skeleton)              │
│                                         │
│  ┌──────┐ ┌──────┐ ┌──────┐             │
│  │ ████ │ │ ████ │ │ ████ │  (Cards)    │
│  │ ████ │ │ ████ │ │ ████ │             │
│  └──────┘ └──────┘ └──────┘             │
│                                         │
│  ████████ (Section title)               │
│  ┌────────────────────┐                 │
│  │ ████████████       │  (Match card)   │
│  │ ████████           │                 │
│  └────────────────────┘                 │
│  ┌────────────────────┐                 │
│  │ ████████████       │                 │
│  │ ████████           │                 │
│  └────────────────────┘                 │
└─────────────────────────────────────────┘
```

**Usage**:
```typescript
if (loading) return <EntityLoadingSkeleton />;
```

---

### EntityErrorAlert

**Purpose**: Generic error state display

**File**: `components/common/EntityErrorAlert.tsx`

**Props**:
```typescript
interface EntityErrorAlertProps {
  error?: string | null;   // Custom error message
  notFound?: boolean;      // Show 404-style message
}
```

**Features**:
- Red alert box with error icon
- Customizable error message
- Default "not found" variant
- Retry button (optional)

**Usage**:
```typescript
// Custom error
<EntityErrorAlert error="Failed to load player data" />

// Not found error
<EntityErrorAlert notFound />
```

**Implementation**:
```typescript
export function EntityErrorAlert({ error, notFound }: EntityErrorAlertProps) {
  if (notFound) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Not Found</AlertTitle>
        <AlertDescription>
          The requested item could not be found.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <Alert variant="destructive">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>Error</AlertTitle>
      <AlertDescription>{error || "An error occurred"}</AlertDescription>
    </Alert>
  );
}
```

---

## Player Components

### PlayerDetail

**Purpose**: Main player detail page with stats and matches

**File**: `components/players/PlayerDetail.tsx`

**Props**:
```typescript
interface PlayerDetailProps {
  playerId: number;
}
```

**State**:
```typescript
const [player, setPlayer] = useState<PlayerStats | null>(null);
const [matches, setMatches] = useState<Match[]>([]);
const [loading, setLoading] = useState(false);
const [matchesLoading, setMatchesLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
const [currentPage, setCurrentPage] = useState(1);
const [totalMatches, setTotalMatches] = useState(0);
const [totalPages, setTotalPages] = useState(1);
```

**Data Fetching**:
```typescript
// Fetch player stats on mount
useEffect(() => {
  const fetchData = async () => {
    try {
      setLoading(true);
      const data = await getPlayerStats(playerId);
      setPlayer(data);
      setError(null);
    } catch (err) {
      setError("Failed to fetch player data");
    } finally {
      setLoading(false);
    }
  };
  fetchData();
}, [playerId]);

// Fetch paginated matches
useEffect(() => {
  const fetchMatches = async () => {
    try {
      setMatchesLoading(true);
      const offset = (currentPage - 1) * ITEMS_PER_PAGE;
      const data = await getPlayerMatches(playerId, {
        limit: ITEMS_PER_PAGE,
        offset,
      });
      setMatches(data.matches);
      setTotalMatches(data.total);
      setTotalPages(Math.ceil(data.total / ITEMS_PER_PAGE));
    } catch (err) {
      console.error("Failed to fetch matches:", err);
    } finally {
      setMatchesLoading(false);
    }
  };
  fetchMatches();
}, [playerId, currentPage]);
```

**Layout**:
```typescript
if (loading) return <PlayerLoadingSkeleton />;
if (error) return <PlayerErrorAlert error={error} />;
if (!player) return <PlayerErrorAlert notFound />;

return (
  <div className="container py-8">
    {/* Header */}
    <div className="mb-8">
      <h1 className="text-4xl font-bold">{player.name}</h1>
      <Badge className="text-lg">
        {player.global_elo} ELO
      </Badge>
    </div>

    {/* Stats Cards */}
    <PlayerStatsCards player={player} />

    {/* Match History */}
    <PlayerMatchesSection
      playerId={playerId}
      matches={matches}
      loading={matchesLoading}
      currentPage={currentPage}
      totalPages={totalPages}
      onPageChange={setCurrentPage}
    />
  </div>
);
```

**Usage**:
```typescript
// app/players/[id]/page.tsx
export default function PlayerPage({ params }) {
  const playerId = parseInt(params.id);
  return <PlayerDetail playerId={playerId} />;
}
```

---

### PlayerStatsCards

**Purpose**: Wrapper for EntityStatsCards with player-specific types

**File**: `components/players/PlayerStatsCards.tsx`

**Props**:
```typescript
interface PlayerStatsCardsProps {
  player: PlayerStats;
}
```

**Implementation**:
```typescript
export function PlayerStatsCards({ player }: PlayerStatsCardsProps) {
  return <EntityStatsCards stats={player} />;
}
```

**Usage**:
```typescript
<PlayerStatsCards player={playerStats} />
```

---

### PlayerMatchesSection

**Purpose**: Wrapper for EntityMatchesSection with player context

**File**: `components/players/PlayerMatchesSection.tsx`

**Props**:
```typescript
interface PlayerMatchesSectionProps {
  playerId: number;
  matches: Match[];
  loading: boolean;
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}
```

**Implementation**:
```typescript
export function PlayerMatchesSection({
  playerId,
  matches,
  loading,
  currentPage,
  totalPages,
  onPageChange,
}: PlayerMatchesSectionProps) {
  return (
    <EntityMatchesSection
      entityId={playerId}
      entityType="player"
      matches={matches}
      loading={loading}
      currentPage={currentPage}
      totalPages={totalPages}
      onPageChange={onPageChange}
    />
  );
}
```

---

### PlayerRegistrationForm

**Purpose**: Form to create new players

**File**: `components/players/PlayerRegistrationForm.tsx`

**Props**:
```typescript
interface PlayerRegistrationFormProps {
  onPlayerRegistered: () => void;  // Callback after successful creation
}
```

**Form Schema**:
```typescript
const formSchema = z.object({
  name: z
    .string()
    .min(2, "Name must be at least 2 characters")
    .max(100, "Name must be less than 100 characters"),
});
```

**Features**:
- React Hook Form with Zod validation
- Real-time field validation
- Duplicate name detection (409 error)
- Toast notifications (Sonner)
- Loading state during submission
- Auto-reset form on success

**Implementation**:
```typescript
export function PlayerRegistrationForm({ onPlayerRegistered }) {
  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: { name: "" },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      await createPlayer(values.name);
      toast.success("Player created successfully!");
      form.reset();
      onPlayerRegistered();
    } catch (error) {
      if (isErrorWithStatus409(error)) {
        toast.error("A player with this name already exists");
        form.setError("name", {
          type: "manual",
          message: "This name is already taken",
        });
      } else {
        toast.error("Failed to create player");
      }
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Player Name</FormLabel>
              <FormControl>
                <Input placeholder="Enter player name" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? "Creating..." : "Create Player"}
        </Button>
      </form>
    </Form>
  );
}
```

**Usage**:
```typescript
<PlayerRegistrationForm onPlayerRegistered={() => router.refresh()} />
```

---

### PlayersList

**Purpose**: Searchable, sortable player directory

**File**: `components/players/PlayersList.tsx`

**Props**:
```typescript
interface PlayersListProps {
  players: Player[];
}
```

**State**:
```typescript
const [searchTerm, setSearchTerm] = useState("");
const [sortKey, setSortKey] = useState<keyof Player>("global_elo");
const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
```

**Features**:
- Client-side search (by name)
- Client-side sorting (by any field)
- Client-side pagination
- useMemo optimization for filtering/sorting
- Responsive grid layout

**Optimization**:
```typescript
const filteredPlayers = useMemo(() => {
  return players.filter((p) =>
    p.name.toLowerCase().includes(searchTerm.toLowerCase())
  );
}, [players, searchTerm]);

const sortedPlayers = useMemo(() => {
  return [...filteredPlayers].sort((a, b) => {
    const aVal = a[sortKey];
    const bVal = b[sortKey];
    if (sortOrder === "asc") {
      return aVal > bVal ? 1 : -1;
    } else {
      return aVal < bVal ? 1 : -1;
    }
  });
}, [filteredPlayers, sortKey, sortOrder]);
```

---

### PlayerLoadingSkeleton

**Purpose**: Player-specific loading state

**File**: `components/players/PlayerLoadingSkeleton.tsx`

**Props**: None

**Implementation**:
```typescript
export function PlayerLoadingSkeleton() {
  return <EntityLoadingSkeleton />;
}
```

---

### PlayerErrorAlert

**Purpose**: Player-specific error state

**File**: `components/players/PlayerErrorAlert.tsx`

**Props**:
```typescript
interface PlayerErrorAlertProps {
  error?: string | null;
  notFound?: boolean;
}
```

**Implementation**:
```typescript
export function PlayerErrorAlert({ error, notFound }: PlayerErrorAlertProps) {
  if (notFound) {
    return (
      <EntityErrorAlert error="Player not found. Please check the player ID." />
    );
  }
  return <EntityErrorAlert error={error || "Failed to load player data"} />;
}
```

---

## Team Components

Team components follow the same pattern as Player components with entity type "team".

### TeamDetail

**File**: `components/teams/TeamDetail.tsx`

**Props**:
```typescript
interface TeamDetailProps {
  teamId: number;
}
```

**Features**: Same as PlayerDetail but for teams

---

### TeamStatsCards

**File**: `components/teams/TeamStatsCards.tsx`

**Implementation**: Wrapper for EntityStatsCards with TeamStats type

---

### TeamMatchesSection

**File**: `components/teams/TeamMatchesSection.tsx`

**Implementation**: Wrapper for EntityMatchesSection with team context

---

### TeamLoadingSkeleton

**File**: `components/teams/TeamLoadingSkeleton.tsx`

**Implementation**: Wrapper for EntityLoadingSkeleton

---

### TeamErrorAlert

**File**: `components/teams/TeamErrorAlert.tsx`

**Implementation**: Wrapper for EntityErrorAlert with team-specific messages

---

## Match Components

### NewMatchPage

**Purpose**: Complex form to create new matches

**File**: `components/matches/NewMatchPage.tsx`

**Props**:
```typescript
interface NewMatchPageProps {
  onMatchCreated?: () => void;  // Callback after creation
  isDialog?: boolean;           // Adjust layout for dialog
}
```

**Form Schema**:
```typescript
const formSchema = z.object({
  winnerPlayer1: z.string().min(1, "Required"),
  winnerPlayer2: z.string().min(1, "Required"),
  loserPlayer1: z.string().min(1, "Required"),
  loserPlayer2: z.string().min(1, "Required"),
  isFanny: z.boolean().default(false),
  playedAt: z.date(),
  notes: z.string().max(500).optional(),
});
```

**Features**:
- Player selection (4 dropdowns with search)
- Team auto-creation (via findOrCreateTeam)
- Date/time picker (defaults to now)
- Fanny checkbox
- Optional notes (max 500 chars)
- Loading states during submission
- Toast notifications
- Redirect to match detail on success

**Workflow**:
1. User selects 4 players (winner team + loser team)
2. Form validates players are unique
3. On submit:
   a. Find or create winner team
   b. Find or create loser team
   c. Create match with teams
   d. Show success toast
   e. Call onMatchCreated callback
   f. Redirect to match detail page

**Implementation Highlights**:
```typescript
async function onSubmit(values: z.infer<typeof formSchema>) {
  try {
    // Step 1: Find or create teams
    const [winnerTeam, loserTeam] = await Promise.all([
      findOrCreateTeam(
        parseInt(values.winnerPlayer1),
        parseInt(values.winnerPlayer2)
      ),
      findOrCreateTeam(
        parseInt(values.loserPlayer1),
        parseInt(values.loserPlayer2)
      ),
    ]);

    // Step 2: Create match
    const match = await createMatch({
      winner_team_id: winnerTeam.team_id,
      loser_team_id: loserTeam.team_id,
      is_fanny: values.isFanny,
      played_at: values.playedAt.toISOString(),
      notes: values.notes,
    });

    toast.success("Match created successfully!");
    onMatchCreated?.();
    router.push(`/matches/${match.match_id}`);
  } catch (error) {
    toast.error("Failed to create match");
  }
}
```

---

### NewMatchDialog

**Purpose**: Dialog wrapper for NewMatchPage

**File**: `components/matches/NewMatchDialog.tsx`

**Props**:
```typescript
interface NewMatchDialogProps {
  trigger?: ReactNode;  // Custom trigger button
}
```

**Features**:
- Controlled dialog state
- Auto-close on successful creation
- Custom trigger button support
- Scrollable content area (max-h-90vh)

**Usage**:
```typescript
<NewMatchDialog trigger={<Button>Record Match</Button>} />
```

**Implementation**:
```typescript
export function NewMatchDialog({ trigger }: NewMatchDialogProps) {
  const [isOpen, setIsOpen] = useState(false);

  const handleMatchCreated = () => {
    setIsOpen(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {trigger || <Button>Create Match</Button>}
      </DialogTrigger>
      <DialogContent className="max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create New Match</DialogTitle>
        </DialogHeader>
        <NewMatchPage onMatchCreated={handleMatchCreated} isDialog={true} />
      </DialogContent>
    </Dialog>
  );
}
```

---

### MatchHistoryUI

**Purpose**: Display list of matches with filters

**File**: `components/matches/MatchHistoryUI.tsx`

**Props**:
```typescript
interface MatchHistoryUIProps {
  matches: Match[];
  loading: boolean;
}
```

**Features**:
- Match cards with winner/loser teams
- Date/time display
- Fanny indicator
- Click to view match details
- Empty state when no matches

---

## Rankings Components

### PlayerRankingsDisplay

**Purpose**: Full rankings page with podium + table

**File**: `components/rankings/PlayerRankingsDisplay.tsx`

**Props**:
```typescript
interface PlayerRankingsDisplayProps {
  players: Player[];
}
```

**Layout**:
```typescript
export function PlayerRankingsDisplay({ players }) {
  const topPlayers = players.slice(0, 3);
  const restPlayers = players.slice(3);

  return (
    <div className="space-y-8">
      {/* Podium for top 3 */}
      <PodiumGrid
        items={topPlayers}
        getKey={(p) => p.player_id}
        getLink={(p) => `/players/${p.player_id}`}
        getName={(p) => p.name}
        getElo={(p) => p.global_elo}
        getWinrate={(p) => `${Math.round(p.win_rate * 100)}%`}
        renderExtra={(p) => (
          <div>{p.wins}W - {p.losses}L</div>
        )}
      />

      {/* Table for rank 4+ */}
      <PlayerRankingTable data={restPlayers} />
    </div>
  );
}
```

---

### PlayerRankingTable

**Purpose**: Player-specific column definitions for RankingTable

**File**: `components/rankings/PlayerRankingTable.tsx`

**Props**:
```typescript
interface PlayerRankingTableProps {
  data: Player[];
  isLoading?: boolean;
  error?: Error | null;
}
```

**Column Definitions**:
```typescript
const columns: ColumnDef<Player>[] = [
  {
    accessorKey: "rank",
    header: () => <div className="text-center">Rank</div>,
    cell: ({ row }) => (
      <div className="text-center font-bold">{row.getValue("rank")}</div>
    ),
  },
  {
    accessorKey: "name",
    header: ({ column }) => (
      <Button variant="ghost" onClick={() => column.toggleSorting()}>
        Name <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    ),
    cell: ({ row }) => (
      <Link href={`/players/${row.original.player_id}`}>
        {row.getValue("name")}
      </Link>
    ),
  },
  {
    accessorKey: "global_elo",
    header: () => <div className="text-center">ELO</div>,
    cell: ({ row }) => (
      <Badge className="font-mono">{row.getValue("global_elo")}</Badge>
    ),
  },
  {
    accessorKey: "matches_played",
    header: () => <div className="text-center">Matches</div>,
    cell: ({ row }) => (
      <div className="text-center">{row.getValue("matches_played")}</div>
    ),
  },
  {
    accessorKey: "win_rate",
    header: () => <div className="text-center">Win Rate</div>,
    cell: ({ row }) => {
      const winRate = row.getValue("win_rate") as number;
      return (
        <div className="text-center">
          {Math.round(winRate * 100)}%
        </div>
      );
    },
  },
];
```

---

### TeamRankingsDisplay

**Purpose**: Full team rankings with podium + table

**File**: `components/rankings/TeamRankingsDisplay.tsx`

**Features**: Same as PlayerRankingsDisplay but for teams

---

### TeamRankingTable

**Purpose**: Team-specific column definitions

**File**: `components/rankings/TeamRankingTable.tsx`

**Column Differences**:
- Displays both player names in team
- Links to team detail page
- Shows team ELO

---

## UI Primitives (ShadCN)

### Overview

**43 ShadCN UI components** provide the design system. These are not documented individually as they follow ShadCN's standard API.

**Location**: `components/ui/`

### Key Components

#### Form Components
- `Form`, `FormField`, `FormItem`, `FormLabel`, `FormControl`, `FormMessage`
- `Input`, `Textarea`, `Select`, `Checkbox`, `RadioGroup`, `Switch`, `Calendar`
- `Button`, `Label`

#### Layout Components
- `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter`
- `Dialog`, `DialogTrigger`, `DialogContent`, `DialogHeader`, `DialogFooter`
- `Sheet`, `Sidebar`, `Separator`
- `AlertDialog`

#### Data Display
- `Table`, `TableHeader`, `TableBody`, `TableRow`, `TableCell`
- `Badge`, `Alert`, `AlertTitle`, `AlertDescription`
- `Skeleton`, `Avatar`

#### Navigation
- `Breadcrumb`, `BreadcrumbList`, `BreadcrumbItem`, `BreadcrumbLink`
- `Pagination`, `PaginationContent`, `PaginationItem`, `PaginationLink`
- `NavigationMenu`, `DropdownMenu`, `Command`

#### Charts (Recharts Integration)
- `ChartContainer`, `ChartTooltip`, `ChartLegend`
- `LineChart`, `PieChart`, `BarChart`

#### Feedback
- `Sonner` (toast notifications)
- `Tooltip`
- `Popover`, `PopoverDialog`

**Documentation**: See [ShadCN UI Docs](https://ui.shadcn.com/docs)

---

## Maintenance Notes

**Update this document when**:
- Adding new components
- Changing component props or API
- Modifying component behavior
- Deprecating components
- Changing design patterns

**Related Documentation**:
- [Frontend Architecture](./09-frontend-architecture.md) - Component hierarchy and patterns
- [Class Diagrams](./07-class-diagrams.md) - Component relationship diagrams
- [Architecture Overview](./01-architecture-overview.md) - Overall system design

---

**Last Updated**: 2025-12-26
**Components Documented**: 31 (excluding ShadCN primitives)
**Total Components**: 74
