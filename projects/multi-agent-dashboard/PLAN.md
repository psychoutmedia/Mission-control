# Gamified Multi-Agent AI Dashboard - Executive Plan

## Tech Stack
- **Three.js** - 3D isometric rendering
- **Electron.js** - Desktop app wrapper
- **React** - UI overlay layer

## Architecture Overview
```
┌─────────────────────────────────────────────────────────┐
│                    ELECTRON MAIN                        │
│         (Window management, native APIs)               │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                 ELECTRON PRELOAD/RENDERER               │
│             (React UI + Three.js Canvas)               │
│  ┌──────────────────┐    ┌──────────────────────────┐   │
│  │   REACT UI       │    │     THREE.JS SCENE       │   │
│  │ • Sign-in Screen │    │ • Isometric Grid        │   │
│  │ • Agent Select   │    │ • Zones (Dev, staging)   │   │
│  │ • Config Panel   │    │ • Avatars (Claude, etc)  │   │
│  │ • Control Panel  │    │ • Anvil/Work stations    │   │
│  └──────────────────┘    │ • Company Sign          │   │
│                          └──────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│              AGENT COORDINATION LAYER                   │
│    (State machine, pathfinding, API integrations)      │
└─────────────────────────────────────────────────────────┘
```

## Phase 1: Project Scaffolding
1. Initialize Electron + React + TypeScript project (Vite)
2. Configure Three.js with React integration (@react-three/fiber)
3. Set up project structure:
   - `src/main/` - Electron main process
   - `src/renderer/` - React UI components
   - `src/scene/` - Three.js scene, cameras, lights
   - `src/agents/` - Agent models, state machines
   - `src/ui/` - Screens (sign-in, select, config)
   - `src/stores/` - State management (Zustand)

## Phase 2: Three.js Scene Foundation
1. Create isometric camera setup (OrthographicCamera)
2. Build grid floor with dark theme
3. Add ambient + directional lighting
4. Create zone boundaries (red outlined areas)
5. Add static objects:
   - Company sign billboard
   - Anvil (work station)
   - Dev stack/folders icon
6. Set up render loop and resize handlers

## Phase 3: Agent System
1. Create base Agent class with:
   - Position (x, y, z)
   - Target position (for movement)
   - State (idle, walking, working)
   - Visual mesh (simple avatar initially)
2. Implement pathfinding (A* or simple lerp for now)
3. Add agent movement with smooth interpolation
4. Create predefined agents:
   - Claude (red cape, sunburst)
   - Codex (white cloak, swirl)
   - Gemini (purple/gold armor)
   - Qwen (ninja style)
   - Cursor (hooded)
   - Molty (red insectoid)
5. Agent state transitions:
   - Idle → Walking (on assignment)
   - Walking → Working (arrived at station)
   - Working → Idle (task complete)

## Phase 4: UI Layer (React)
1. Sign-in screen (company name, login)
2. Agent selection modal:
   - Grid of agent cards
   - Hover states, selection
   - "Recruit" button
3. Agent config panel (side/drawer):
   - Connection settings (SSH, gateway URL)
   - Auto-connect toggle
   - Test/Cancel/Save buttons
4. Control sidebar (left):
   - Home, Hand (select), Map (zones), Flask (experimental), Globe

## Phase 5: Interactivity & Integration
1. Clickable zones → highlight on hover
2. Agent dragging (simple position update)
3. Click sign → trigger UI flow
4. UI → Scene communication (Zustand store)
5. Real-time agent status updates

## Phase 6: Polish & Assets
1. Replace simple geometry with actual 3D models
2. Add animations (walking bob, idle breathing)
3. Particle effects (agent active indicator)
4. Shadows and ambient occlusion
5. Responsive layout

## File Structure
```
├── electron/
│   └── main.ts           # Electron main process
├── src/
│   ├── main.tsx          # React entry point
│   ├── App.tsx           # Root component
│   ├── scene/
│   │   ├── index.tsx     # Three.js canvas setup
│   │   ├── Camera.ts     # Isometric camera
│   │   ├── Floor.ts      # Grid floor
│   │   ├── Zones.ts      # Zone boundaries
│   │   └── Objects.ts    # Sign, anvil, etc
│   ├── agents/
│   │   ├── index.ts      # Agent factory
│   │   ├── Agent.tsx     # Individual agent mesh
│   │   └── types.ts      # Agent interfaces
│   ├── ui/
│   │   ├── screens/
│   │   │   ├── SignIn.tsx
│   │   │   ├── AgentSelect.tsx
│   │   │   └── ConfigPanel.tsx
│   │   └── components/
│   ├── stores/
│   │   └── useStore.ts   # Zustand state
│   └── assets/
│       └── models/       # 3D model files
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## Development Phases (Build Order)
1. **Week 1:** Scaffolding + Basic 3D scene
2. **Week 2:** Agent system + movement
3. **Week 3:** React UI overlay
4. **Week 4:** Interactivity + polish
5. **Week 5:** API integrations + deployment
