"""
Astra-MUD: Database Layer
SQLite persistence for world state
"""

import aiosqlite
import json
from pathlib import Path
from typing import Optional
from .models import World, Room, Item, NPC, Player, Position


DB_PATH = Path(__file__).parent.parent / "data" / "world.db"


async def init_db(db_path: str = str(DB_PATH)):
    """Initialize database schema."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    async with aiosqlite.connect(db_path) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS rooms (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS npcs (
                id TEXT PRIMARY KEY,
                data TEXT NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS players (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                data TEXT NOT NULL
            );
            
            CREATE INDEX IF NOT EXISTS idx_players_name ON players(name);
            CREATE INDEX IF NOT EXISTS idx_items_location ON items(data);
        """)
        await db.commit()


def _room_from_dict(data: dict) -> Room:
    pos = data.get("position", {})
    return Room(
        id=data["id"],
        name=data["name"],
        description=data["description"],
        position=Position(pos.get("x", 0), pos.get("y", 0), pos.get("z", 0)),
        exits=data.get("exits", {}),
        items=data.get("items", []),
        npcs=data.get("npcs", []),
        properties=data.get("properties", {}),
    )


def _npc_from_dict(data: dict) -> NPC:
    from datetime import datetime
    return NPC(
        id=data["id"],
        name=data["name"],
        description=data["description"],
        room_id=data["room_id"],
        personality=data.get("personality", {}),
        inventory=data.get("inventory", []),
        memory=data.get("memory", []),
        relationships=data.get("relationships", {}),
        ai_model=data.get("ai_model", "phi3"),
        is_alive=data.get("is_alive", True),
        properties=data.get("properties", {}),
    )


def _item_from_dict(data: dict) -> Item:
    return Item(
        id=data["id"],
        name=data["name"],
        description=data["description"],
        location=data["location"],
        item_type=data.get("item_type", "misc"),
        properties=data.get("properties", {}),
    )


def _player_from_dict(data: dict) -> Player:
    return Player(
        id=data["id"],
        name=data["name"],
        room_id=data["room_id"],
        inventory=data.get("inventory", []),
        hp=data.get("hp", 100),
        max_hp=data.get("max_hp", 100),
        properties=data.get("properties", {}),
    )


async def load_world(db_path: str = str(DB_PATH)) -> World:
    """Load entire world from database."""
    world = World()
    
    if not Path(db_path).exists():
        await init_db(db_path)
        return world
    
    async with aiosqlite.connect(db_path) as db:
        # Load rooms
        async with db.execute("SELECT data FROM rooms") as cursor:
            async for row in cursor:
                room = _room_from_dict(json.loads(row[0]))
                world.add_room(room)
        
        # Load items
        async with db.execute("SELECT data FROM items") as cursor:
            async for row in cursor:
                item = _item_from_dict(json.loads(row[0]))
                world.add_item(item)
        
        # Load NPCs
        async with db.execute("SELECT data FROM npcs") as cursor:
            async for row in cursor:
                npc = _npc_from_dict(json.loads(row[0]))
                world.add_npc(npc)
        
        # Load players
        async with db.execute("SELECT data FROM players") as cursor:
            async for row in cursor:
                player = _player_from_dict(json.loads(row[0]))
                world.add_player(player)
    
    return world


async def save_room(db_path: str, room: Room):
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "INSERT OR REPLACE INTO rooms (id, data) VALUES (?, ?)",
            (room.id, json.dumps(room.to_dict()))
        )
        await db.commit()


async def save_npc(db_path: str, npc: NPC):
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "INSERT OR REPLACE INTO npcs (id, data) VALUES (?, ?)",
            (npc.id, json.dumps(npc.to_dict()))
        )
        await db.commit()


async def save_player(db_path: str, player: Player):
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "INSERT OR REPLACE INTO players (id, name, data) VALUES (?, ?, ?)",
            (player.id, player.name, json.dumps(player.to_dict()))
        )
        await db.commit()


async def save_item(db_path: str, item: Item):
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            "INSERT OR REPLACE INTO items (id, data) VALUES (?, ?)",
            (item.id, json.dumps(item.to_dict()))
        )
        await db.commit()


async def create_starter_world(db_path: str = str(DB_PATH)):
    """Create a starter world with a basic dungeon."""
    await init_db(db_path)
    world = World()
    
    # Create entrance
    entrance = Room(
        id="entrance",
        name="Dungeon Entrance",
        description="You stand at the mouth of an ancient dungeon. Cold air drifts from within. A moss-covered stone archway marks the entrance.",
        exits={"north": "hallway", "outside": "wild"},
    )
    
    # Create hallway
    hallway = Room(
        id="hallway",
        name="Torch-Lit Corridor",
        description="A narrow corridor stretches before you. Flickering torches cast dancing shadows on the stone walls. Strange symbols are carved into the rocks.",
        exits={"south": "entrance", "north": "chamber", "east": "armory"},
    )
    
    # Create chamber
    chamber = Room(
        id="chamber",
        name="Grand Chamber",
        description="A vast chamber opens before you. Ancient columns rise to a ceiling lost in darkness. Something glints in the shadows to the north.",
        exits={"south": "hallway", "north": "treasury"},
    )
    
    # Create armory
    armory = Room(
        id="armory",
        name="Ruined Armory",
        description="Weapon racks line the walls, most empty or rusted beyond use. A single sword gleams on a pedestal.",
        exits={"west": "hallway"},
    )
    
    # Create treasury
    treasury = Room(
        id="treasury",
        name="Dragon's Hoard",
        description="Mountains of gold coins and glittering gems fill this chamber. Atop the hoard sleeps an ancient gold dragon.",
        exits={"south": "chamber"},
    )
    
    # Add rooms to world
    world.add_room(entrance)
    world.add_room(hallway)
    world.add_room(chamber)
    world.add_room(armory)
    world.add_room(treasury)
    
    # Create items
    from .models import Item
    sword = Item(
        id="rusty_sword",
        name="Rusty Sword",
        description="An old but serviceable sword. Perfectly balanced for combat.",
        location="armory",
        item_type="weapon",
        properties={"damage": 10, "durability": 50},
    )
    
    potion = Item(
        id="health_potion",
        name="Health Potion",
        description="A red liquid swirls in a glass vial. It smells of herbs and honey.",
        location="hallway",
        item_type="consumable",
        properties={"heals": 30},
    )
    
    gold = Item(
        id="gold_coins",
        name="Gold Coins",
        description="A small pile of ancient gold coins, stamped with a dragon sigil.",
        location="treasury",
        item_type="misc",
        properties={"value": 100},
    )
    
    world.add_item(sword)
    world.add_item(potion)
    world.add_item(gold)
    
    # Create NPCs
    from .models import NPC
    guard = NPC(
        id="skeleton_guard",
        name="Skeleton Guard",
        description="An undead warrior, still clad in ancient armor. Empty eye sockets glow with unholy light.",
        room_id="hallway",
        personality={
            "traits": ["hostile", "protective"],
            "goals": "Defend the dungeon from intruders",
            "mood": "eternal vigilance",
        },
        ai_model="phi3",
    )
    
    dragon = NPC(
        id="gold_dragon",
        name="Ancient Dragon",
        description="A massive gold dragon, scales glittering like treasure itself. Its eyes are closed in ancient slumber.",
        room_id="treasury",
        personality={
            "traits": ["sleeping", "powerful", "intelligent"],
            "goals": "Protect its hoard",
            "mood": "dormant",
        },
        ai_model="phi3",
    )
    
    world.add_npc(guard)
    world.add_npc(dragon)
    
    # Save everything
    for room in world.rooms.values():
        await save_room(db_path, room)
    for item in world.items.values():
        await save_item(db_path, item)
    for npc in world.npcs.values():
        await save_npc(db_path, npc)
    
    return world
