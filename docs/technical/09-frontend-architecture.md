# Frontend Architecture

**Document Type**: Technical Architecture Guide
**Target Audience**: Frontend developers, UI/UX engineers
**Last Updated**: 2025-12-26
**Maintained By**: Development Team

---

## Table of Contents

1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Directory Structure](#directory-structure)
4. [Component Hierarchy](#component-hierarchy)
5. [Data Fetching Strategy](#data-fetching-strategy)
6. [State Management](#state-management)
7. [Routing & Navigation](#routing--navigation)
8. [Design System](#design-system)
9. [Performance Optimization](#performance-optimization)
10. [Common Patterns](#common-patterns)

---

## Overview

The Baby Foot ELO frontend is built with **Next.js 16 App Router** and follows a component-driven architecture. The application emphasizes simplicity, code reuse through generic components, and direct API integration without complex state management libraries.

### Architecture Principles

1. **Component Reusability**: Generic wrapper pattern for shared logic
2. **Local State Management**: No global state libraries (Redux, Zustand)
3. **Direct API Calls**: Axios-based services, no SWR caching layer
4. **Server Components First**: Leverage Next.js App Router for server-side rendering
5. **Progressive Enhancement**: Works without JavaScript, enhanced with client interactivity

### Key Characteristics

- **45+ React components** organized by domain (players, teams, matches, rankings)
- **43 ShadCN UI primitives** for consistent design system
- **Client-side data fetching** with `useEffect` and `useState`
- **TanStack Table** for sortable/filterable tables
- **Recharts** for ELO trend visualization
- **React Hook Form + Zod** for form validation
- **Tailwind CSS** for styling with dark mode support

---

## Technology Stack

### Core Framework

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 16.x | React framework with App Router |
| **React** | 19.x | UI library |
| **TypeScript** | 5.x | Type safety |
| **Tailwind CSS** | 3.x | Utility-first styling |

### Data & State

| Library | Purpose |
|---------|---------|
| **Axios** | HTTP client for API calls |
| **React Hook Form** | Form state management |
| **Zod** | Schema validation |

### UI Components

| Library | Purpose |
|---------|---------|
| **ShadCN UI** | Base component library (31 components) |
| **TanStack Table** | Advanced data tables |
| **Recharts** | Chart visualization |
| **Sonner** | Toast notifications |
| **Lucide React** | Icon library |

### Development Tools

| Tool | Purpose |
|------|---------|
| **Bun** | Package manager and runtime |
| **ESLint** | Code linting |
| **Prettier** | Code formatting |
| **Vitest** | Unit testing |

---

## Directory Structure

```text
/
├── app/                          # Next.js App Router (pages & API routes)
│   ├── layout.tsx               # Root layout with providers
│   ├── page.tsx                 # Home page (player rankings)
│   ├── globals.css              # Global styles & Tailwind imports
│   │
│   ├── players/                 # Player routes
│   │   └── [id]/
│   │       └── page.tsx         # Player detail page
│   │
│   ├── teams/                   # Team routes
│   │   └── [id]/
│   │       └── page.tsx         # Team detail page
│   │
│   ├── matches/                 # Match routes
│   │   ├── page.tsx             # Match history page
│   │   └── new/
│   │       └── page.tsx         # Create match page
│   │
│   └── api/v1/                  # API routes (backend)
│       ├── health/
│       ├── players/
│       ├── teams/
│       └── matches/
│
├── components/                   # React components (organized by domain)
│   ├── ui/                      # ShadCN UI primitives (31 components)
│   ├── common/                  # Generic reusable components
│   ├── players/                 # Player-specific components
│   ├── teams/                   # Team-specific components
│   ├── matches/                 # Match-specific components
│   ├── rankings/                # Rankings display components
│   ├── app-sidebar.tsx          # Main navigation
│   ├── Header.tsx               # Page header
│   ├── ThemeProvider.tsx        # Dark mode context
│   └── ThemeToggle.tsx          # Theme switcher
│
├── lib/                         # Shared utilities
│   ├── api/
│   │   └── client/              # Frontend API client services
│   │       ├── playerService.ts # Player API calls
│   │       ├── teamService.ts   # Team API calls
│   │       └── matchService.ts  # Match API calls
│   └── utils.ts                 # Utility functions (cn(), etc.)
│
├── types/                       # TypeScript type definitions
│   ├── player.types.ts
│   ├── team.types.ts
│   ├── match.types.ts
│   └── stats.types.ts
│
├── hooks/                       # Custom React hooks
│   └── use-mobile.ts            # Responsive breakpoint detection
│
└── public/                      # Static assets
    └── fonts/                   # Custom fonts (Geist)
```

---

## Component Hierarchy

### Layer 1: Layout Components

These provide the application shell and global UI elements:

```text
app/layout.tsx (Root Layout)
├── ThemeProvider                 # Dark mode context
├── SidebarProvider               # Sidebar state management
│   ├── AppSidebar               # Main navigation sidebar
│   │   ├── Logo                 # Championship trophy icon
│   │   ├── SidebarContent
│   │   │   ├── Rankings (Players/Teams)
│   │   │   ├── New Match
│   │   │   ├── Match History
│   │   │   └── Admin Section
│   │   └── SidebarFooter (Theme toggle)
│   │
│   └── SidebarInset             # Main content area
│       ├── Header               # Page header with breadcrumbs
│       └── {children}           # Page content
│
└── Toaster                      # Toast notification container
```

**File Locations**:
- `app/layout.tsx:1` - Root layout
- `components/app-sidebar.tsx:1` - Navigation sidebar
- `components/Header.tsx:1` - Page header
- `components/ThemeProvider.tsx:1` - Theme context

---

### Layer 2: Page Components

Top-level route components that orchestrate data fetching and layout:

```text
app/page.tsx                     # Home: Player rankings
app/players/[id]/page.tsx        # Player detail page
app/teams/[id]/page.tsx          # Team detail page
app/matches/page.tsx             # Match history
app/matches/new/page.tsx         # Create match form
```

**Data Fetching Pattern** (Server Component):
```typescript
// app/page.tsx - Home page
export default async function HomePage() {
  // Fetch on server (SSR)
  const players = await getPlayerRankings();

  return <PlayerRankingsDisplay players={players} />;
}
```

**Client Component Pattern** (Detail Pages):
```typescript
// app/players/[id]/page.tsx
'use client';

export default function PlayerPage({ params }: { params: { id: string } }) {
  const playerId = parseInt(params.id);

  return <PlayerDetail playerId={playerId} />;
}
```

---

### Layer 3: Feature Components

Domain-specific components that handle feature logic and state:

#### Player Components (`components/players/`)

```text
PlayerDetail.tsx                 # Main detail page (stateful)
├── PlayerLoadingSkeleton        # Loading state
├── PlayerErrorAlert             # Error state
└── (Data loaded)
    ├── Header with name & ELO badge
    ├── PlayerStatsCards         # 3-card stats display
    │   └── EntityStatsCards     # Generic stats implementation
    └── PlayerMatchesSection     # Match history with pagination
        └── EntityMatchesSection # Generic matches implementation
```

**State Management**:
```typescript
// PlayerDetail.tsx pattern
const [player, setPlayer] = useState<PlayerStats | null>(null);
const [matches, setMatches] = useState<Match[]>([]);
const [loading, setLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
const [currentPage, setCurrentPage] = useState(1);

// Two useEffect hooks: initial data + paginated matches
useEffect(() => { /* Fetch player stats */ }, [playerId]);
useEffect(() => { /* Fetch matches */ }, [playerId, currentPage]);
```

**File**: `components/players/PlayerDetail.tsx:1`

#### Team Components (`components/teams/`)

```text
TeamDetail.tsx                   # Main detail page (stateful)
TeamStatsCards → EntityStatsCards
TeamMatchesSection → EntityMatchesSection
TeamLoadingSkeleton
TeamErrorAlert
```

**File**: `components/teams/TeamDetail.tsx:1`

#### Match Components (`components/matches/`)

```text
NewMatchPage.tsx                 # Complex match creation form
├── Team selection (winner/loser)
├── Date/time picker
├── Fanny checkbox
├── Notes textarea
└── Submit handler (creates match + updates ELO)

NewMatchDialog.tsx               # Dialog wrapper for NewMatchPage
MatchHistoryUI.tsx               # Match list display
```

**File**: `components/matches/NewMatchPage.tsx:1`

---

### Layer 4: Generic Components

Reusable components that work with any entity type through TypeScript generics:

#### EntityStatsCards (`components/common/EntityStatsCards.tsx`)

**Purpose**: Display 3-card stats layout (ELO hero, chart, winrate)

```typescript
interface EntityStatsCardsProps {
  stats: EntityStats;  // Generic type
}

// Used by:
// - PlayerStatsCards (wrapper)
// - TeamStatsCards (wrapper)
```

**Layout**:
```text
┌─────────────────────────────────────────────────┐
│  ELO Hero Card          ELO Evolution Chart     │
│  ┌──────────────┐       ┌──────────────┐        │
│  │ 1650 ELO     │       │ Line Chart   │        │
│  │ +24 trend    │       │ (Recharts)   │        │
│  └──────────────┘       └──────────────┘        │
│                                                  │
│  Winrate Donut Chart                             │
│  ┌──────────────┐                                │
│  │ Pie Chart    │  W-L record summary            │
│  └──────────────┘                                │
└─────────────────────────────────────────────────┘
```

**File**: `components/common/EntityStatsCards.tsx:1`

---

#### EntityMatchesSection (`components/common/EntityMatchesSection.tsx`)

**Purpose**: Paginated match history grouped by date

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
```

**Features**:
- Groups matches by date (`YYYY-MM-DD`)
- Displays match cards with winner/loser teams
- Shows ELO change badges (green for gain, red for loss)
- Pagination controls (previous/next, page numbers)

**File**: `components/common/EntityMatchesSection.tsx:1`

---

#### RankingTable (`components/common/RankingTable.tsx`)

**Purpose**: Generic sortable/filterable table using TanStack Table

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
- Responsive design (scrollable on mobile)

**Used by**:
- `PlayerRankingTable` (defines player columns)
- `TeamRankingTable` (defines team columns)

**File**: `components/common/RankingTable.tsx:1`

---

#### PodiumGrid (`components/common/PodiumGrid.tsx`)

**Purpose**: Championship-styled top 3 display

```typescript
function PodiumGrid<T>({
  items: T[];
  getKey: (item: T) => React.Key;
  getLink: (item: T) => string;
  getName: (item: T) => ReactNode;
  getElo: (item: T) => ReactNode;
  getWinrate: (item: T) => ReactNode;
  renderExtra?: (item: T) => ReactNode;
}): JSX.Element
```

**Layout** (Responsive Grid):
```text
Desktop:
┌──────────────────────────────────────────┐
│  🥈 Silver     🥇 Gold      🥉 Bronze    │
│  #2            #1           #3           │
│  Player 2      Player 1     Player 3     │
│  1580 ELO      1650 ELO     1520 ELO     │
│  72% WR        68% WR       65% WR       │
└──────────────────────────────────────────┘

Mobile:
┌────────────┐
│  🥇 Gold   │
│  #1        │
│  Player 1  │
│  1650 ELO  │
│  68% WR    │
├────────────┤
│  🥈 Silver │
│  ...       │
├────────────┤
│  🥉 Bronze │
│  ...       │
└────────────┘
```

**Styling**:
- Gold: `bg-gradient-to-br from-yellow-400 to-yellow-600`
- Silver: `bg-gradient-to-br from-gray-300 to-gray-500`
- Bronze: `bg-gradient-to-br from-amber-600 to-amber-800`
- Hover animations: `hover:scale-105 transition-transform`

**File**: `components/common/PodiumGrid.tsx:1`

---

### Layer 5: UI Primitives (ShadCN)

**31 ShadCN UI components** provide the design system foundation:

#### Form Components
- `Form`, `FormField`, `FormItem`, `FormLabel`, `FormControl`, `FormMessage`
- `Input`, `Textarea`, `Select`, `Checkbox`, `RadioGroup`, `Switch`
- `Button`, `Label`

#### Layout Components
- `Card`, `CardHeader`, `CardTitle`, `CardContent`, `CardFooter`
- `Dialog`, `DialogTrigger`, `DialogContent`, `DialogHeader`, `DialogFooter`
- `Sheet`, `Sidebar`, `Separator`

#### Data Display
- `Table`, `TableHeader`, `TableBody`, `TableRow`, `TableCell`
- `Badge`, `Alert`, `AlertTitle`, `AlertDescription`
- `Skeleton`, `Avatar`

#### Navigation
- `Breadcrumb`, `BreadcrumbList`, `BreadcrumbItem`, `BreadcrumbLink`
- `Pagination`, `PaginationContent`, `PaginationItem`, `PaginationLink`

#### Charts
- `ChartContainer`, `ChartTooltip`, `ChartLegend`
- `LineChart`, `PieChart` (Recharts integration)

**Directory**: `components/ui/`

---

## Data Fetching Strategy

### No SWR - Direct Axios Approach

**Important**: This application does NOT use SWR. All data fetching is done with Axios and manual state management.

### API Client Services

**Location**: `lib/api/client/`

Three service files provide typed API calls:

#### playerService.ts

```typescript
const API_URL = "/api/v1";

export const getPlayers = async (params?: GetPlayersParams): Promise<Player[]> => {
  const response = await axios.get(`${API_URL}/players`, { params });
  return response.data;
};

export const getPlayerById = async (playerId: number): Promise<Player> => { ... };
export const createPlayer = async (name: string): Promise<Player> => { ... };
export const getPlayerRankings = async (): Promise<Player[]> => { ... };
export const getPlayerStats = async (playerId: number): Promise<PlayerStats> => { ... };
export const getPlayerMatches = async (
  playerId: number,
  params?: GetPlayerMatchesParams
): Promise<MatchHistory> => { ... };
```

**6 functions** for player-related API calls.

**File**: `lib/api/client/playerService.ts:1`

---

#### teamService.ts

```typescript
export const getTeamRankings = async (): Promise<Team[]> => { ... };
export const findOrCreateTeam = async (
  player1Id: number,
  player2Id: number
): Promise<Team> => { ... };
export const getTeamById = async (teamId: number): Promise<Team> => { ... };
export const getTeamStatistics = async (teamId: number): Promise<TeamStats> => { ... };
export const getTeamMatches = async (
  teamId: number,
  params?: GetTeamMatchesParams
): Promise<Match[]> => { ... };
```

**5 functions** for team-related API calls.

**File**: `lib/api/client/teamService.ts:1`

---

#### matchService.ts

```typescript
export const getMatches = async (
  options?: MatchFilterOptions
): Promise<Match[]> => { ... };

export const createMatch = async (
  matchData: BackendMatchCreatePayload
): Promise<Match> => { ... };
```

**2 functions** for match-related API calls.

**File**: `lib/api/client/matchService.ts:1`

---

### Data Fetching Patterns

#### Pattern 1: Server Component (SSR)

```typescript
// app/page.tsx - Home page
export default async function HomePage() {
  // Fetch on server during SSR
  const players = await getPlayerRankings();

  // Pass data as props to client component
  return <PlayerRankingsDisplay players={players} />;
}
```

**Benefits**:
- Fast initial page load (data pre-rendered)
- SEO-friendly (content in HTML)
- No loading spinner on first visit

**File**: `app/page.tsx:1`

---

#### Pattern 2: Client Component with useEffect

```typescript
// components/players/PlayerDetail.tsx
'use client';

export default function PlayerDetail({ playerId }: Props) {
  const [player, setPlayer] = useState<PlayerStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  if (loading) return <PlayerLoadingSkeleton />;
  if (error) return <PlayerErrorAlert error={error} />;
  if (!player) return <PlayerErrorAlert notFound />;

  return <div>...</div>;
}
```

**Benefits**:
- Simple and predictable
- Easy to debug (clear state transitions)
- No caching complexity

**Drawbacks**:
- No automatic caching (refetch on every mount)
- No background revalidation
- Manual loading/error state management

**File**: `components/players/PlayerDetail.tsx:1`

---

#### Pattern 3: Paginated Data Fetching

```typescript
// components/players/PlayerDetail.tsx (continued)
const [matches, setMatches] = useState<Match[]>([]);
const [matchesLoading, setMatchesLoading] = useState(false);
const [currentPage, setCurrentPage] = useState(1);
const [totalMatches, setTotalMatches] = useState(0);
const [totalPages, setTotalPages] = useState(1);

const ITEMS_PER_PAGE = 10;

// Separate useEffect for paginated matches
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

**Features**:
- Offset-based pagination
- Manual total calculation
- Independent loading state for matches
- Refetch on page change

---

### Error Handling in API Calls

```typescript
// Type guard for 409 Conflict errors
function isErrorWithStatus409(error: unknown): error is AxiosError {
  return axios.isAxiosError(error) && error.response?.status === 409;
}

// Usage in form submission
try {
  await createPlayer(name);
  toast.success("Player created!");
} catch (error) {
  if (isErrorWithStatus409(error)) {
    toast.error("Player name already exists");
    form.setError("name", {
      type: "manual",
      message: "This name is already taken",
    });
  } else if (axios.isAxiosError(error)) {
    toast.error(error.response?.data?.detail || "Failed to create player");
  } else {
    toast.error("An unexpected error occurred");
  }
}
```

**File**: `components/players/PlayerRegistrationForm.tsx:1`

---

## State Management

### No Global State Library

**Philosophy**: Keep state local and simple

**What's NOT used**:
- ❌ Redux
- ❌ Zustand
- ❌ Jotai
- ❌ React Context for app state (only for theme)

### Local State with useState

Each component manages its own state:

```typescript
// PlayerDetail.tsx state
const [player, setPlayer] = useState<PlayerStats | null>(null);
const [matches, setMatches] = useState<Match[]>([]);
const [loading, setLoading] = useState(false);
const [matchesLoading, setMatchesLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
const [currentPage, setCurrentPage] = useState(1);
const [totalMatches, setTotalMatches] = useState(0);
const [totalPages, setTotalPages] = useState(1);
```

### Context API (Theme Only)

```typescript
// components/ThemeProvider.tsx
export function ThemeProvider({ children }: ThemeProviderProps) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      {children}
    </NextThemesProvider>
  );
}
```

**Usage**:
```typescript
import { useTheme } from "next-themes";

const { theme, setTheme } = useTheme();
```

**File**: `components/ThemeProvider.tsx:1`

---

### Form State with React Hook Form

```typescript
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";

const formSchema = z.object({
  name: z.string().min(2, "Minimum 2 characters").max(100),
});

export function PlayerRegistrationForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { name: "" },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      await createPlayer(values.name);
      toast.success("Player created!");
      form.reset();
    } catch (error) {
      // Error handling
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
                <Input placeholder="Enter name" {...field} />
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

**File**: `components/players/PlayerRegistrationForm.tsx:1`

---

## Routing & Navigation

### Next.js App Router

**Route Structure**:

```text
app/
├── page.tsx                     # / (Home - player rankings)
├── players/
│   └── [id]/
│       └── page.tsx             # /players/:id (Player detail)
├── teams/
│   └── [id]/
│       └── page.tsx             # /teams/:id (Team detail)
├── matches/
│   ├── page.tsx                 # /matches (Match history)
│   └── new/
│       └── page.tsx             # /matches/new (Create match)
└── api/v1/                      # /api/v1/* (API routes)
```

### Navigation Component

```typescript
// components/app-sidebar.tsx
export function AppSidebar() {
  return (
    <Sidebar>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <Link href="/">
              <Trophy className="h-6 w-6" />
              <span>Baby Foot Championship</span>
            </Link>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Rankings</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link href="/">
                    <Users className="h-4 w-4" />
                    <span>Players</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link href="/teams">
                    <UsersRound className="h-4 w-4" />
                    <span>Teams</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>Matches</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link href="/matches/new">
                    <PlusCircle className="h-4 w-4" />
                    <span>New Match</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link href="/matches">
                    <History className="h-4 w-4" />
                    <span>Match History</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <ThemeToggle />
      </SidebarFooter>
    </Sidebar>
  );
}
```

**File**: `components/app-sidebar.tsx:1`

---

### Programmatic Navigation

```typescript
import { useRouter } from 'next/navigation';

function MyComponent() {
  const router = useRouter();

  const handleNavigate = () => {
    router.push('/players/123');
    // or router.back(), router.forward(), router.refresh()
  };
}
```

---

## Design System

### Color Palette (Tailwind Config)

**File**: `tailwind.config.ts`

```typescript
theme: {
  extend: {
    colors: {
      // Brand colors
      championship: {
        gold: '#FFD700',
        silver: '#C0C0C0',
        bronze: '#CD7F32',
      },

      // ELO trend colors (CSS variables)
      win: 'hsl(var(--win))',      // Green (#22C55E)
      lose: 'hsl(var(--lose))',    // Red (#EF4444)

      // ShadCN color system
      background: 'hsl(var(--background))',
      foreground: 'hsl(var(--foreground))',
      primary: 'hsl(var(--primary))',
      secondary: 'hsl(var(--secondary))',
      // ... etc
    },
  },
}
```

**CSS Variables** (`app/globals.css`):
```css
:root {
  --win: 142 71% 45%;           /* Green */
  --lose: 0 84% 60%;            /* Red */
  --match-win-bg: 142 76% 36%;  /* Dark green */
  --match-lose-bg: 0 72% 51%;   /* Dark red */
}

.dark {
  --win: 142 70% 45%;
  --lose: 0 84% 60%;
  /* ... dark mode overrides */
}
```

---

### Typography

**Font Family**: Geist (local font)

```typescript
// app/layout.tsx
import { GeistSans } from 'geist/font/sans';

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={GeistSans.className}>
      <body>{children}</body>
    </html>
  );
}
```

**Font Sizes** (Tailwind defaults):
- `text-xs`: 0.75rem (12px)
- `text-sm`: 0.875rem (14px)
- `text-base`: 1rem (16px)
- `text-lg`: 1.125rem (18px)
- `text-xl`: 1.25rem (20px)
- `text-2xl`: 1.5rem (24px)
- `text-3xl`: 1.875rem (30px)
- `text-4xl`: 2.25rem (36px)

---

### Component Styling Patterns

#### Card Styling

```tsx
<Card className="overflow-hidden border-2 shadow-lg hover:shadow-xl transition-shadow">
  <CardHeader className="bg-gradient-to-r from-blue-500 to-purple-600">
    <CardTitle className="text-white">Title</CardTitle>
  </CardHeader>
  <CardContent className="pt-6">
    Content
  </CardContent>
</Card>
```

#### Badge Styling (ELO Trends)

```tsx
<Badge
  variant={eloChange > 0 ? "default" : "destructive"}
  className={eloChange > 0 ? "bg-win" : "bg-lose"}
>
  {eloChange > 0 ? `+${eloChange}` : eloChange}
</Badge>
```

#### Button Variants

```tsx
<Button variant="default">Primary</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="destructive">Delete</Button>
```

---

### Dark Mode Support

**Theme Toggle**:
```typescript
// components/ThemeToggle.tsx
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

**File**: `components/ThemeToggle.tsx:1`

---

## Performance Optimization

### Current Optimizations

1. **Server-Side Rendering** (Next.js App Router)
   - Home page pre-rendered with player rankings
   - Faster initial page load
   - Better SEO

2. **Client-Side Memoization**
   ```typescript
   // components/players/PlayersList.tsx
   const filteredPlayers = useMemo(() => {
     return players.filter(p =>
       p.name.toLowerCase().includes(searchTerm.toLowerCase())
     );
   }, [players, searchTerm]);

   const sortedPlayers = useMemo(() => {
     return [...filteredPlayers].sort((a, b) => {
       // Sort logic based on sortKey
     });
   }, [filteredPlayers, sortKey, sortOrder]);
   ```

3. **Code Splitting** (Next.js automatic)
   - Route-based code splitting
   - Dynamic imports for large components

4. **Image Optimization** (Next.js Image component)
   - Not currently used (no images in app)
   - Ready for future image additions

### Potential Optimizations (Not Implemented)

- **SWR/React Query**: Add caching layer for API calls
- **Virtual Scrolling**: For very long player/team lists
- **Debounced Search**: Optimize search input
- **Intersection Observer**: Lazy load match cards

---

## Common Patterns

### Pattern 1: Generic Wrapper

**Problem**: Duplicate code for player and team components

**Solution**: Create generic component, wrap with specific types

```typescript
// Generic implementation
function EntityStatsCards<T extends EntityStats>({ stats }: { stats: T }) {
  return <div>...</div>;
}

// Player-specific wrapper
function PlayerStatsCards({ player }: { player: PlayerStats }) {
  return <EntityStatsCards stats={player} />;
}

// Team-specific wrapper
function TeamStatsCards({ team }: { team: TeamStats }) {
  return <EntityStatsCards stats={team} />;
}
```

**Benefits**:
- Single source of truth for logic
- Type safety maintained
- Easy to modify all instances at once

---

### Pattern 2: Loading/Error/Data States

**Problem**: Consistent handling of async states

**Solution**: Standardized state transition components

```typescript
function MyComponent() {
  if (loading) return <EntityLoadingSkeleton />;
  if (error) return <EntityErrorAlert error={error} />;
  if (!data) return <EntityErrorAlert notFound />;

  return <div>{/* Render data */}</div>;
}
```

---

### Pattern 3: Compound Components

**Problem**: Complex component configuration

**Solution**: Use composition with child components

```typescript
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>
    Content
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

---

### Pattern 4: Render Props

**Problem**: Dynamic rendering based on data

**Solution**: Pass rendering functions as props

```typescript
<PodiumGrid
  items={players}
  getKey={(player) => player.player_id}
  getLink={(player) => `/players/${player.player_id}`}
  getName={(player) => player.name}
  getElo={(player) => player.global_elo}
  renderExtra={(player) => (
    <div>W-L record: {player.wins}-{player.losses}</div>
  )}
/>
```

---

### Pattern 5: Dialog with Form

**Problem**: Modal forms with state management

**Solution**: Dialog wrapper with controlled state

```typescript
function NewMatchDialog({ trigger }: { trigger?: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);

  const handleMatchCreated = () => {
    setIsOpen(false);  // Close on success
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        {trigger || <Button>Create Match</Button>}
      </DialogTrigger>
      <DialogContent className="max-h-[90vh] overflow-y-auto">
        <NewMatchPage
          onMatchCreated={handleMatchCreated}
          isDialog={true}
        />
      </DialogContent>
    </Dialog>
  );
}
```

---

## Maintenance Notes

**Update this document when**:
- Adding new component patterns
- Changing data fetching strategy (e.g., adding SWR)
- Modifying state management approach
- Adding new UI libraries
- Changing routing structure
- Implementing performance optimizations

**Related Documentation**:
- [Architecture Overview](./01-architecture-overview.md) - Overall system architecture
- [Component Reference](./10-component-reference.md) - Individual component docs
- [API Reference](./08-api-reference.md) - Backend API endpoints
- [Class Diagrams](./07-class-diagrams.md) - Component hierarchy diagrams

---

**Last Updated**: 2025-12-26
**Components Documented**: 45+
**UI Primitives**: 31 (ShadCN)
