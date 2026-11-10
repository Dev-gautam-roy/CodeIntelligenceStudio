# Design Specification — Code Intelligence Studio

## 1. Design Philosophy
Code Intelligence Studio is an engineering-first platform tailored for software developers, architects, and DevOps professionals. The design philosophy centers on **clarity, high information density, low latency, and zero ambiguity**.

Key pillars:
1. **Instrument Panel Aesthetic**: Clean dark-mode first design inspired by professional IDEs, flight decks, and telemetry stations.
2. **Deterministic Feedback**: Every operation displays explicit states (`PENDING`, `RUNNING`, `WAITING_FOR_APPROVAL`, `COMPLETED`, `FAILED`).
3. **Graph-Centric Navigation**: Deep architectural relationships and multi-agent workflows are visualized visually with interactive node networks.
4. **Safety Prominence**: Actions that modify code, create pull requests, or alter remote repositories are styled with high-contrast safety badges and explicit approval modals.

---

## 2. Color Palette & Theming

The application defaults to a refined Dark Slate engineering palette with high-contrast semantics compliant with WCAG 2.1 AA (minimum 4.5:1 contrast for text).

### Neutral Tones
- **Background Root (`bg-root`)**: `#0B0F17` (Deep Obsidian Void)
- **Surface Elevation 1 (`bg-surface-1`)**: `#111827` (Panel background, sidebar)
- **Surface Elevation 2 (`bg-surface-2`)**: `#1F2937` (Card backgrounds, modals)
- **Surface Elevation 3 (`bg-surface-3`)**: `#374151` (Dropdowns, active node borders)
- **Border Default (`border-default`)**: `#1E293B`
- **Border Focused (`border-focus`)**: `#3B82F6`

### Text Colors
- **Text Primary**: `#F9FAFB` (High contrast headers and values)
- **Text Secondary**: `#9CA3AF` (Descriptions, labels, timestamps)
- **Text Muted**: `#6B7280` (Hints, placeholders, secondary tags)

### Semantic & Status Colors
- **Primary / Brand Accent**: `#3B82F6` (`blue-500` / Glow: `rgba(59, 130, 246, 0.2)`)
- **Success / Completed**: `#10B981` (`emerald-500`)
- **Warning / Waiting Approval**: `#F59E0B` (`amber-500` - pulse animation on waiting gates)
- **Destructive / Error / Failed**: `#EF4444` (`red-500`)
- **Information / Agent Running**: `#8B5CF6` (`violet-500` - subtle border pulse)

---

## 3. Typography & Hierarchy

### Font Families
- **Display & UI Body**: `Inter`, `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- **Code & Telemetry**: `JetBrains Mono`, `Fira Code`, `Consolas, monospace`

### Scale
- **H1 / Page Title**: `24px` (`1.5rem`), SemiBold (600), Line Height: 1.25
- **H2 / Section Title**: `18px` (`1.125rem`), Medium (500), Line Height: 1.3
- **H3 / Card Header**: `15px` (`0.9375rem`), Medium (500), Line Height: 1.4
- **Body Regular**: `13px` (`0.8125rem`), Regular (400), Line Height: 1.5
- **Small / Metadata**: `11px` (`0.6875rem`), Regular (400), Line Height: 1.4
- **Monospace Code**: `12px` (`0.75rem`), Regular (400), Line Height: 1.6

---

## 4. Layout & Navigation Hierarchy

### Root Shell Structure
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Header: Project Status • Model Provider • Active Repo • Approval Badge (3)   │
├──────────────┬──────────────────────────────────────────────────────────────┤
│ Sidebar Nav  │ Main Workspace Panel                                         │
│              │                                                              │
│ • Overview   │ ┌──────────────────────────────────────────────────────────┐ │
│ • Repos      │ │ Dynamic View (e.g. Architecture Graph, Workflow DAG)     │ │
│ • Agents     │ │                                                          │ │
│ • Workflows  │ └──────────────────────────────────────────────────────────┘ │
│ • Testing    │ ┌───────────────────────────┬──────────────────────────────┐ │
│ • Security   │ │ Agent Card Rail           │ Interactive Terminal Panel   │ │
│ • Terminal   │ │ (Live Agent Metrics)      │ (Real-time logs & streaming) │ │
│ • Settings   │ └───────────────────────────┴──────────────────────────────┘ │
└──────────────┴──────────────────────────────────────────────────────────────┘
```

---

## 5. Component Standards

### 5.1 Repository Action Bar
A prominent sticky toolbar at the top of the repository interface:
- **URL Input**: Monospace placeholder with automatic validation icon (Green check on valid GitHub syntax, Red alert on malformed paths).
- **Action Dropdown**: Options:
  - `Analyze Architecture`
  - `Clone & Ingest`
  - `Fork Repository`
  - `Run Test Suite`
  - `Debug Failures`
  - `Security Audit`
  - `Prepare Contribution`
  - `Validate Deployment`
- **Execute Button**: Blue pill with high-contrast icon and loading spinner during execution.

### 5.2 Agent Card Rail
Horizontal or grid cards displaying the status of active agents:
- **Header**: Agent Title (e.g., `TestingAgent`) + Status Pill (`IDLE`, `RUNNING`, `DONE`).
- **Telemetry**: Token Counter, Elapsed Execution Time (e.g., `1.84s`), Active Task ID.
- **Summary Snippet**: Last parsed milestone or error message.

### 5.3 React Flow Graph Visualization
- **Node Styles**:
  - Module/File Nodes: Dark slate cards with icon tags indicating language/framework.
  - Dependency Edges: Smooth Bézier curves with directional arrows; red dashed lines for circular dependencies.
  - Workflow Task Nodes: Color-coded state borders with approval pause icons.
- **MiniMap & Controls**: Pan, zoom, fit-to-screen, and node inspector drawer on node click.

### 5.4 Terminal Console
- Fixed-height or collapsible bottom tray simulating a high-performance shell.
- Real-time streaming output with ANSI color support.
- Output filter toggles: `[All]`, `[Agent Logs]`, `[Stdout/Stderr]`, `[Errors Only]`.

---

## 6. Accessibility & Responsiveness
- **Keyboard Navigation**: Full `Tab` order traversing sidebar navigation, form inputs, action dropdowns, and modal dialogs.
- **Screen Reader Support**: Semantic HTML tags (`<nav>`, `<main>`, `<aside>`, `<header>`) and `aria-live="polite"` for background task updates.
- **Responsive Breakpoints**:
  - Desktop (>1280px): Multi-column layout with persistent sidebar and split graphs.
  - Tablet (768px - 1279px): Collapsible icon-only sidebar, stacked panels.
  - Mobile (<768px): Overlay menu, focused single-card views.
