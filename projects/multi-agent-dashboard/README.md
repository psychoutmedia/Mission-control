# Multi-Agent Dashboard

A gamified AI agent management dashboard built with Three.js, React, and Electron.

## Features
- 🎮 Isometric 3D view of your AI workforce
- 🤖 Visualize agents (Claude, Codex, Gemini, etc.) as avatars
- 📍 Zone-based organization (Development, staging, etc.)
- 🖱️ Click-to-interact with agents and zones
- 🎨 Dark theme with red accents

## Tech Stack
- **Three.js** + **React Three Fiber** - 3D rendering
- **React** + **TypeScript** - UI layer
- **Zustand** - State management
- **Electron** - Desktop wrapper (ready to add)

## Getting Started

```bash
cd projects/multi-agent-dashboard
npm install
npm run dev
```

## Development

```bash
# Start dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
├── src/
│   ├── main.tsx         # Entry point
│   ├── App.tsx          # Root component + Canvas
│   ├── scene/           # Three.js scene components
│   │   ├── index.tsx    # Scene composition
│   │   ├── Floor.tsx    # Grid floor
│   │   ├── Zones.tsx    # Zone boundaries
│   │   └── StaticObjects.tsx  # Sign, anvil, etc
│   ├── agents/          # Agent system
│   │   ├── Agent.tsx    # Individual agent mesh
│   │   └── index.ts     # Agent types & factory
│   ├── ui/              # React UI overlay
│   │   ├── index.tsx    # UI wrapper
│   │   ├── components/  # Sidebar, etc
│   │   └── screens/     # SignIn, AgentSelect, Config
│   └── stores/          # Zustand state
│       └── useStore.ts  # Global state
├── electron/            # Electron main process
├── index.html
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## Screens

1. **Sign In** - Enter company name
2. **Dashboard** - Main 3D view with agents
3. **Agent Select** - Recruit new agents
4. **Config Panel** - Configure agent settings

## Controls

- Click sign to open menu
- Sidebar navigation (Home, Hand, Map, Flask, Globe)
- Agent status indicators (green = active)

## Next Steps

- [ ] Add Electron main process
- [ ] Implement agent movement/pathfinding
- [ ] Add 3D models for agents
- [ ] Connect to real AI APIs
- [ ] Add drag-and-drop
- [ ] Animations and particles
