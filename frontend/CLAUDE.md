# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Dream Journal Frontend — a React + TypeScript SPA for a Jungian dream analysis platform. Features AI-powered dream extraction, agentic chat, interactive knowledge graph visualization, and analytics. Built with Vite, Tailwind CSS, React Query, and React Router.

## Commands

```bash
# Install dependencies
npm install

# Dev server (port 3000, proxies /api to localhost:8000)
npm run dev

# Type-check + production build
npm run build

# Preview production build
npm run preview
```

No test framework, linter, or formatter is currently configured.

## Architecture

### Routing (App.tsx)

```
/login              — Public (redirects to / if authenticated)
/                   — Dashboard
/dreams             — Dream journal list
/dreams/new         — Create dream (2-step wizard)
/dreams/:id         — Dream detail view
/dreams/:id/edit    — Edit dream (reuses NewDream component)
/chat               — AI chat with dream agent
/graph              — Force-directed knowledge graph
/analytics          — Analytics dashboard
/symbols            — Symbol library
/characters         — Character library
```

All routes except `/login` are protected and wrapped in `<Layout>` (sidebar + header + outlet).

### Key Directories

- `src/lib/api.ts` — Axios client + all API modules (`dreamsApi`, `chatApi`, `graphApi`, `analyticsApi`, `symbolsApi`, `charactersApi`)
- `src/lib/auth.tsx` — AuthContext provider, JWT in localStorage, axios interceptors for token injection and 401 handling
- `src/hooks/useApi.ts` — React Query hooks wrapping every API call (staleTime: 5min, retry: 1)
- `src/components/ui/` — Reusable UI primitives (Button, Card, Badge, Input, Modal, Spinner, etc.)
- `src/components/layout/` — Layout, Sidebar, Header
- `src/pages/` — Route-level page components
- `src/styles/globals.css` — Tailwind base + custom component classes (`.card`, `.btn-*`, `.input`, `.badge-*`, `.chat-message-*`, etc.)

### State Management

- **Server state**: React Query for all data fetching and mutations. No Redux/Zustand.
- **Auth state**: React Context (`useAuth()`)
- **No other global state** — components use local state and URL params.

### API Client (lib/api.ts)

Base URL: `/api` (Vite proxies to `http://localhost:8000`). Request interceptor adds `Authorization: Bearer <token>`. Response interceptor catches 401 → clears token → redirects to `/login`.

### Dream Creation Flow (NewDream.tsx)

Two-step wizard:
1. **Write**: User enters narrative, metadata, emotions → calls `POST /extract/preview` for AI extraction
2. **Review & Edit**: Displays extracted symbols/characters/themes/emotions, all editable by user → calls `POST /extract/create`

AI interpretation is hidden by default to prevent over-reliance. Personal interpretation is emphasized.

### Demo Mode

Activated via `?demo=true` URL param or `switchToDemo()`. Stores `demo_mode` flag in localStorage, calls `/auth/demo` for a token. Shows banner with "Exit Demo" button.

## Styling

Obsidian-inspired dark theme defined in `tailwind.config.js`:
- **Background**: `#0f0f0f` / Surface: `#1a1a1a` / Accent: `#8b5cf6` (purple)
- **Fonts**: Inter (sans), JetBrains Mono (mono) — loaded via Google Fonts in `index.html`
- **Semantic colors**: `emotion-joy`, `emotion-fear`, `emotion-sadness`, `archetype-shadow`, `archetype-anima`, etc.
- Custom component classes in `globals.css` (`.card`, `.btn-primary`, `.input`, `.badge-accent`, `.tag-symbol`, `.chat-message-user`, `.nav-item`, `.text-gradient`, `.glass`)

## Conventions

- **Path alias**: `@/` maps to `src/` (configured in vite.config.ts and tsconfig.json)
- **Exports**: Barrel files (`index.ts`) in `components/ui/`, `components/layout/`, `pages/`, `hooks/`
- **Icons**: Lucide React — `w-4 h-4` inline, `w-5 h-5` in headers
- **API list responses**: `{ data, has_more, next_cursor }` pattern
- **Query keys**: `['dreams']`, `['dream', id]`, `['analytics-summary']`, etc.
- **Mutations**: Invalidate related queries on success (e.g., creating a dream invalidates `['dreams']`)

## Key Libraries

| Library | Purpose |
|---------|---------|
| @tanstack/react-query | Server state, caching, mutations |
| react-router-dom 6 | Client-side routing |
| axios | HTTP client with interceptors |
| recharts | Charts in Analytics/Dashboard |
| react-force-graph-2d | Interactive knowledge graph |
| @radix-ui/* | Dialog, dropdown, select, tabs, toast |
| class-variance-authority | Component variant definitions (Button) |
| date-fns | Date formatting |
| clsx + tailwind-merge | Conditional class merging (`cn()` in lib/utils.ts) |
