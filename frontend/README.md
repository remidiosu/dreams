# Dream Journal Frontend

A beautiful, Obsidian-inspired dark theme frontend for the Dream Journal GraphRAG application.

## Features

- 🌙 **Dark Theme** - Obsidian-inspired design with purple accents
- 📊 **Dashboard** - Overview of your dream journaling activity
- ✏️ **Dream Editor** - Record and edit dreams with emotions, symbols, characters
- 💬 **AI Chat** - Query your dream patterns using GraphRAG
- 🕸️ **Knowledge Graph** - Visualize connections between dream elements
- 📈 **Analytics** - Charts and insights about your dream patterns
- 🔮 **Jungian Analysis** - Archetype tracking and individuation progress

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast builds
- **Tailwind CSS** for styling
- **React Query** for data fetching
- **Recharts** for analytics charts
- **Lucide Icons** for beautiful icons
- **React Router** for navigation

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running on port 8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

## Project Structure

```
src/
├── components/
│   ├── ui/          # Reusable UI components
│   ├── layout/      # Layout components (Sidebar, Header)
│   ├── dreams/      # Dream-specific components
│   ├── chat/        # Chat components
│   ├── graph/       # Graph visualization
│   └── analytics/   # Chart components
├── pages/           # Route pages
├── hooks/           # Custom React hooks
├── lib/             # API client, auth, utilities
└── styles/          # Global CSS and Tailwind config
```

## Pages

| Page | Path | Description |
|------|------|-------------|
| Dashboard | `/` | Overview with stats, recent dreams, activity chart |
| Dreams | `/dreams` | List of all dreams with search |
| Dream Detail | `/dreams/:id` | View single dream with all details |
| New Dream | `/dreams/new` | Create new dream entry |
| Chat | `/chat` | AI-powered dream analysis chat |
| Graph | `/graph` | Knowledge graph visualization |
| Analytics | `/analytics` | Charts and pattern insights |
| Symbols | `/symbols` | Symbol library |
| Characters | `/characters` | Character library |
| Login | `/login` | Authentication |

## Design System

### Colors

- **Background**: `#0f0f0f` (deep black)
- **Surface**: `#1a1a1a` (cards, panels)
- **Accent**: `#8b5cf6` (purple)
- **Secondary**: `#6366f1` (indigo)

### Components

The UI is built with custom Tailwind components:
- `btn-primary`, `btn-secondary`, `btn-ghost`
- `input`, `textarea`, `select`
- `card`, `card-hover`
- `tag-symbol`, `tag-emotion`, `tag-character`
- `badge-default`, `badge-accent`, `badge-success`

## API Integration

The frontend connects to the backend API through a proxy in development:
- Frontend: `localhost:3000`
- API: `localhost:8000`
- Proxy: `/api/*` → `localhost:8000/*`

## License

MIT