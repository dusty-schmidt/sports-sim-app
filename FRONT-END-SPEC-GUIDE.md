This is a comprehensive technical specification document designed to sit at the root of your frontend repository. It translates your functional requirements into actionable architectural directives, component structures, and state management strategies for your development team.

-----

**File Location:** `project_root/FRONTEND_SPECIFICATION.md`
**Description:** Technical specifications and architectural guidelines for the frontend application, mapping functional requirements to component design and state management logic.

-----

# Frontend Technical Specification: Sports Analytics & Optimization Platform

## 1\. Architecture Overview & Tech Stack

Based on the `fastapi-full-stack` template, this frontend utilizes **React**. To support high-performance data manipulation and complex state, the following library decisions are enforced:

  * **Component System:** Chakra UI (inherited from template) or Tailwind CSS for layout.
  * **Data Grid:** `TanStack Table` (Headless UI) is required for the Player Pool to handle virtualization, sorting, and custom cell renderers (sparklines, inputs).
  * **State Management:**
      * **Server State:** `TanStack Query` (React Query) for fetching model data, projections, and live scores.
      * **Client State:** `Zustand` for managing user overrides, lineup construction rules, and global settings.
  * **Visualization:** `Recharts` or `Nivo` for distribution histograms and exposure bars.

-----

## 2\. Core Modules & Component Breakdown

### I. The Player Pool (Data Grid)

**Directory:** `src/components/PlayerGrid`

This is the primary workspace. It must handle dense data display without rendering lag.

**Key Components:**

  * `PlayerGrid.tsx`: The main wrapper. Implements row virtualization (rendering only visible rows) to support datasets of 500+ players.
  * `OutcomeToggle.tsx`: A segmented control switching the visible data context.
      * *States:* `Mean` | `Floor (25th)` | `Ceiling (85th)`
      * *Logic:* Switching this updates the value displayed in the `Projection` column but preserves the user's manual overrides.
  * `EditableCell.tsx`: A custom cell renderer.
      * *Logic:* Checks if a `user_override` exists for this `player_id`. If yes, render yellow background. If no, render default model background.
      * *Interaction:* `onBlur` or `Enter` commits the change to the local Zustand store.
  * `ActionCell.tsx`: Contains the hover-visible toolbelt.
      * *Icons:* Lock (Force 100%), Exclude (Force 0%), Boost (Multiplier).
  * `DistributionSparkline.tsx`: A lightweight SVG bar chart rendered *inside* the cell showing the probability curve of the player's outcomes.

### II. Configuration & Rules Engine

**Directory:** `src/components/OptimizerConfig`

**Key Components:**

  * `CorrelationBuilder.tsx`: A dynamic form builder.
      * *UX:* "If [Primary Player] is selected, [REQUIRE/EXCLUDE] [N] players from [Same Team/Opponent]."
  * `VarianceSlider.tsx`: A standard range input (0-100).
      * *Logic:* Updates the `uniqueness_threshold` parameter sent to the Python backend.
  * `GlobalFilter.tsx`: A faceted filter sidebar.
      * *Features:* Checkbox groups for Game Time, Team, and Injury Status.

### III. Exposure Management (Portfolio View)

**Directory:** `src/components/ExposureDashboard`

This view is reactive. Changes here trigger recalculations or re-sorting of the lineup batch.

**Key Components:**

  * `ExposureRow.tsx`:
      * *Visual:* A horizontal progress bar representing current ownership %.
      * *Inputs:* `Min_Input` and `Max_Input`.
      * *Validation:* `Max` cannot be less than `Min`.
  * `GroupConstraint.tsx`: A generic wrapper for Position or Team caps.
      * *Example:* "NYG Players \<= 40%".
      * *Visual:* Tags similar to Jira labels that can be added/removed.

### IV. Lineup & Bet Management

**Directory:** `src/components/LineupViewer`

**Key Components:**

  * `LineupCard.tsx`: Displays a single lineup/bet slip.
      * *Header:* Projected ROI / Win Prob.
      * *Body:* List of players/legs.
  * `SmartSwapModal.tsx`: The most complex UI interaction.
      * *Input:* An array of `lineup_ids` and the `player_id` to remove.
      * *Async Logic:* Fetches a list of valid replacement players from the backend who fit the remaining salary cap and position slots for *all* selected lineups.
  * `ExportButton.tsx`:
      * *Dropdown:* Options for specific sportsbook/DFS formats (e.g., DraftKings CSV, FanDuel CSV).
      * *Action:* Formats JSON data to CSV string and writes to `navigator.clipboard` or triggers download.

### V. Live/State Tracking

**Directory:** `src/components/LiveTracker`

**Key Components:**

  * `GameTicker.tsx`: A banner or sidebar component.
      * *Logic:* Subscribes to a WebSocket or high-frequency polling endpoint.
  * `StatusBadge.tsx`: A reusable UI chip.
      * *Variant Map:*
          * `LOCKED`: Red, Padlock icon.
          * `PPD`: Grey, Warning icon.
          * `ACTIVE`: Green, Pulse animation.

-----

## 3\. Data Models & State Logic (TypeScript)

To ensure modularity and alignment, strict TypeScript interfaces must be used.

### The "Override" Pattern

We do not mutate the raw model data. We layer user data on top.

```typescript
// The raw data from the simulation/model backend
interface PlayerModelData {
  id: string;
  name: string;
  team: string;
  salary: number;
  stats: {
    mean_projection: number;
    floor_25: number;
    ceiling_85: number;
    win_probability: number; // For bets
  };
  status: "ACTIVE" | "QUESTIONABLE" | "OUT" | "LOCKED";
}

// The user's local edits
interface UserOverride {
  manual_projection?: number; // If defined, ignore model stats
  lock_status?: "LOCKED" | "EXCLUDED" | "NONE";
  exposure_min?: number;
  exposure_max?: number;
  sentiment_boost?: number; // e.g., 1.1x multiplier
}

// The Derived View (What the Grid actually renders)
type GridRow = PlayerModelData & UserOverride & {
  is_edited: boolean; // Computed flag for UI styling (yellow bg)
  display_projection: number; // The final number used for optimization
};
```

### Smart Swap Logic

When performing the Bulk Smart Swap, the frontend must send the context of the swap to the backend to get valid replacements.

```typescript
interface SwapRequest {
  target_lineup_ids: string[];
  player_out_id: string;
  // The frontend does not calculate valid swaps locally due to complex 
  // multi-lineup salary constraints. It asks the backend.
}

interface SwapResponse {
  valid_replacements: PlayerModelData[]; // List of players who fit ALL target lineups
}
```

-----

## 4\. UX/UI Interaction Flows

### The "Edit -\> Rebuild" Loop

1.  User clicks a cell in **Player Pool** and changes a projection from `15.5` to `20.0`.
2.  Zustand store updates `UserOverride` map.
3.  The specific cell turns yellow.
4.  User navigates to **Configuration** and hits "Build Lineups."
5.  Frontend sends `ModelData + UserOverrides` to the Python backend.
6.  Backend returns generated lineups.
7.  User is redirected to **Exposure Management** view.

### The "Exposure Cap" Loop

1.  In **Exposure Management**, user sees "LeBron James" is in 80% of lineups.
2.  User types "50" into the "Max %" input.
3.  **UI Feedback:** The input saves immediately. A "Re-optimize needed" warning banner appears (since removing lineups might require generating new ones to fill the void).
4.  User clicks "Refresh/Rebalance."
5.  Frontend requests a re-sort/swap from the backend to satisfy the new constraint.

-----

## 5\. Next Steps for Development

1.  **Scaffold the Store:** Create the Zustand store to handle the `UserOverride` logic before building any UI.
2.  **Grid Prototype:** Implement the `TanStack Table` with just the standard columns and one editable column to prove the "Yellow Background" concept works.
3.  **Mock Data:** Generate a JSON file with 100 fake players to test the "Percentile Toggle" performance.

-----

**Would you like me to generate the TypeScript code for the Zustand store (Step 1) so you can drop it immediately into your project?**