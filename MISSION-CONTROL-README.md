# Mission Control - File-Based Edition 🎯

Mission Control now uses a **file-based backend** so Astra can manage your tasks directly!

## Quick Start

### 1. Start the server
```bash
cd ~/clawd
./start-mission-control.sh
```

Or manually:
```bash
node mission-control-server.js
```

### 2. Open in browser
Go to: **http://localhost:8888**

The board now syncs with `mission-control-data.json` automatically!

## CLI Commands (for Astra)

Astra can now manage tasks via the command line:

### Add a task
```bash
./mc add "Research DeepSeek R1" --column backlog --tag coding
./mc add "Daily briefing setup" --column inprogress
```

### List tasks
```bash
./mc list                    # All tasks
./mc list --column backlog   # Just backlog
```

### Move a task
```bash
./mc move TASK_ID review
```

### Delete a task
```bash
./mc delete TASK_ID
```

## How It Works

- **Data file**: `mission-control-data.json`
- **Server**: Node.js server on port 8888
- **Browser**: Loads from server API, auto-refreshes every 5 seconds
- **Astra**: Edits JSON file directly, browser picks up changes

## Features

✅ **Live sync** - Changes appear in browser within 5 seconds  
✅ **Drag & drop** - Move tasks between columns  
✅ **Delete tasks** - Custom confirmation modal  
✅ **Export** - Download backups  
✅ **Filters** - Filter by tag  
✅ **CLI access** - Astra can manage tasks programmatically  

## Example Workflow

**You (in browser):**
1. Create task "Build AI agent"
2. Drag to "In Progress"

**Astra (via CLI):**
```bash
./mc add "Study transformers architecture" --column backlog --tag coding
./mc move 123456 review  # Mark your task complete
```

**Result:** Both changes appear in the browser automatically! 🚀

## Troubleshooting

**Server won't start?**
- Check if port 8888 is in use: `lsof -i :8888`
- Try a different port in `mission-control-server.js`

**Browser can't connect?**
- Make sure the server is running
- Check the console for errors
- Try refreshing with Cmd+Shift+R

**Tasks not updating?**
- Server should auto-reload changes
- Browser refreshes every 5 seconds
- Click the 🔄 Refresh button manually

## Files

- `mission-control.html` - The dashboard (served by server)
- `mission-control-server.js` - Node.js API server
- `mission-control-data.json` - Your task data
- `mc` - CLI tool for task management
- `start-mission-control.sh` - Quick start script
