"""
Astra-MUD: Web Server
Starlette WebSocket server for real-time gameplay
"""

import asyncio
import json
from pathlib import Path
from collections.abc import MutableMapping
from starlette.applications import Starlette
from starlette.routing import Route, WebSocketRoute
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from world.database import load_world, save_npc, save_player, create_starter_world
from world.models import World
from npcs.brain import NPCBrain


# Global world state
world: World = None
brains: dict[str, NPCBrain] = {}
DB_PATH = Path(__file__).parent.parent / "data" / "world.db"


async def get_room_description(room, world: World) -> str:
    """Build rich room description."""
    desc = f"**{room.name}**\n\n{r.room.description}\n"
    
    # Exits
    if room.exits:
        exits = ", ".join(room.exits.keys())
        desc += f"\n*Exits: {exits}*\n"
    
    # Items
    items = [world.get_item(i) for i in room.items if world.get_item(i)]
    if items:
        item_names = ", ".join(f"*{i.name}*" for i in items)
        desc += f"\n*You see: {item_names}*\n"
    
    # NPCs
    npcs = [world.get_npc(n) for n in room.npcs if world.get_npc(n)]
    if npcs:
        npc_names = ", ".join(f"*{n.name}*" for n in npcs)
        desc += f"\n*Present: {npc_names}*\n"
    
    return desc


class GameSession:
    """Manages a single player connection."""
    
    def __init__(self, websocket: WebSocket, player_id: str, player_name: str):
        self.websocket = websocket
        self.player_id = player_id
        self.player_name = player_name
        self.room_id = "entrance"  # Starting room
    
    async def send(self, message: str):
        """Send message to player."""
        await self.websocket.send_text(json.dumps({"type": "message", "content": message}))
    
    async def send_room(self):
        """Send current room description."""
        room = world.get_room(self.room_id)
        if room:
            desc = await get_room_description(room, world)
            await self.send(desc)
    
    async def handle_command(self, command: str):
        """Process player command."""
        global world
        
        cmd = command.strip().lower()
        
        # Movement
        if cmd in ["n", "north"]:
            await self.do_move("north")
        elif cmd in ["s", "south"]:
            await self.do_move("south")
        elif cmd in ["e", "east"]:
            await self.do_move("east")
        elif cmd in ["w", "west"]:
            await self.do_move("west")
        elif cmd in ["u", "up"]:
            await self.do_move("up")
        elif cmd in ["d", "down"]:
            await self.do_move("down")
        
        # Look
        elif cmd in ["look", "l"]:
            await self.send_room()
        
        # Say
        elif cmd.startswith("say "):
            message = cmd[4:]
            await self.handle_say(message)
        
        # Talk to NPC
        elif cmd.startswith("talk to ") or cmd.startswith("talk "):
            npc_name = cmd.replace("talk to ", "").replace("talk ", "").strip()
            await self.handle_talk(npc_name)
        
        # Inventory
        elif cmd in ["inventory", "inv", "i"]:
            await self.handle_inventory()
        
        # Help
        elif cmd in ["help", "h", "?"]:
            await self.send("""**Commands:**
- `n/s/e/w` - Move north/south/east/west
- `look` - Examine room
- `say [message]` - Speak aloud
- `talk to [npc]` - Talk to an NPC
- `inventory` - Check your belongings
- `help` - Show this message""")
        
        else:
            await self.send(f"You can't do that.")
    
    async def do_move(self, direction: str):
        """Move to adjacent room."""
        room = world.get_room(self.room_id)
        if not room:
            await self.send("You seem lost...")
            return
        
        if direction not in room.exits:
            await self.send(f"You can't go {direction} from here.")
            return
        
        target_room_id = room.exits[direction]
        target_room = world.get_room(target_room_id)
        
        if not target_room:
            await self.send("The path leads into darkness...")
            return
        
        self.room_id = target_room_id
        
        # Update player position
        player = world.get_player(self.player_id)
        if player:
            player.room_id = target_room_id
            await save_player(str(DB_PATH), player)
        
        await self.send(f"\n*You travel {direction}...*\n")
        await self.send_room()
    
    async def handle_say(self, message: str):
        """Handle player speaking."""
        room = world.get_room(self.room_id)
        if not room:
            return
        
        await self.send(f"You say: {message}")
        
        # NPCs react
        for npc_id in room.npcs:
            npc = world.get_npc(npc_id)
            if npc and npc_id in brains:
                brain = brains[npc_id]
                context = f"The player '{self.player_name}' just said: '{message}'"
                response = await brain.think(f"The player says: {message}", context)
                if response:
                    await self.send(f"\n*{npc.name} responds: {response}*\n")
    
    async def handle_talk(self, npc_name: str):
        """Handle talking to specific NPC."""
        room = world.get_room(self.room_id)
        if not room:
            return
        
        npc = world.get_npc_by_name(npc_name, self.room_id)
        if not npc:
            await self.send(f"There's no one called '{npc_name}' here.")
            return
        
        # Check if we have a brain for this NPC
        if npc.id not in brains:
            # Create brain
            brains[npc.id] = NPCBrain(
                npc_id=npc.id,
                name=npc.name,
                personality=npc.personality,
                ai_model=npc.ai_model,
            )
        
        brain = brains[npc.id]
        
        # Build context
        context = f"""Current room: {room.name}
{npc.name} is here. They are {npc.personality.get('mood', 'neutral')}."""

        await self.send(f"\nYou approach {npc.name} and strike up a conversation...")
        
        response = await brain.think(
            f"The player '{self.player_name}' wants to talk. Start a conversation as {npc.name}.",
            context
        )
        
        await self.send(f"\n*{npc.name}: {response}*\n")
        
        # Update NPC last interaction
        npc.last_interaction = datetime.utcnow()
        await save_npc(str(DB_PATH), npc)
    
    async def handle_inventory(self):
        """Show player inventory."""
        player = world.get_player(self.player_id)
        if not player:
            await self.send("You carry nothing.")
            return
        
        if not player.inventory:
            await self.send("Your pockets are empty.")
            return
        
        items = [world.get_item(i) for i in player.inventory if world.get_item(i)]
        item_list = "\n".join(f"- *{i.name}*: {i.description}" for i in items)
        await self.send(f"**Inventory:**\n{item_list}")


# Store active sessions
sessions: dict[str, GameSession] = {}


async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections."""
    await websocket.accept()
    
    # Send welcome
    await websocket.send_text(json.dumps({
        "type": "welcome",
        "content": """**Welcome to Astra-MUD** 🏰
An LLM-powered text adventure

Type `help` for commands."""
    }))
    
    # Simple login - just ask for name
    await websocket.send_text(json.dumps({
        "type": "message",
        "content": "What is your name, adventurer?"
    }))
    
    # Wait for name
    try:
        data = await websocket.receive_text()
        player_name = data.strip()
    except:
        await websocket.close()
        return
    
    # Create or get player
    player = world.get_player_by_name(player_name)
    if not player:
        from world.models import Player
        import uuid
        player = Player(
            id=str(uuid.uuid4()),
            name=player_name,
            room_id="entrance",
        )
        world.add_player(player)
        await save_player(str(DB_PATH), player)
    
    session = GameSession(websocket, player.id, player_name)
    sessions[player.id] = session
    
    await session.send_room()
    
    # Main game loop
    try:
        while True:
            data = await websocket.receive_text()
            await session.handle_command(data)
    except WebSocketDisconnect:
        sessions.pop(player.id, None)


async def homepage(request):
    """Serve the game client."""
    html_path = Path(__file__).parent / "templates" / "game.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text())
    return HTMLResponse("<h1>Astra-MUD</h1><p>Game client not found.</p>")


async def startup():
    """Initialize world on startup."""
    global world
    
    print("🏰 Astra-MUD Starting...")
    
    if DB_PATH.exists():
        print("Loading world from database...")
        world = await load_world(str(DB_PATH))
        print(f"Loaded {len(world.rooms)} rooms, {len(world.npcs)} NPCs, {len(world.players)} players")
    else:
        print("Creating new world...")
        world = await create_starter_world(str(DB_PATH))
        print(f"Created world with {len(world.rooms)} rooms")
    
    # Initialize brains for NPCs
    for npc_id, npc in world.npcs.items():
        brains[npc_id] = NPCBrain(
            npc_id=npc.id,
            name=npc.name,
            personality=npc.personality,
            ai_model=npc.ai_model,
        )
    
    print("Ready!")


@asynccontextmanager
async def lifespan(app):
    await startup()
    yield


# Create app
app = Starlette(
    routes=[
        Route("/", homepage),
        WebSocketRoute("/ws", websocket_endpoint),
    ],
    lifespan=lifespan,
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
