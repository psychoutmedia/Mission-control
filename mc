#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).parent / "mission-control-data.json"

def load_data():
    if not DATA_FILE.exists():
        return {"tasks": [], "activity": []}
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_activity(data, action, task_title):
    data['activity'].insert(0, {
        'action': action,
        'taskTitle': task_title,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })
    if len(data['activity']) > 10:
        data['activity'] = data['activity'][:10]

def cmd_add(args):
    """Add a new task: mc add "Task title" [--column COLUMN] [--tag TAG]"""
    if not args or args[0].startswith('--'):
        print("Usage: mc add \"Task title\" [--column COLUMN] [--tag TAG]")
        return
    
    title = args[0]
    column = 'backlog'
    tag = ''
    
    i = 1
    while i < len(args):
        if args[i] == '--column' and i + 1 < len(args):
            column = args[i + 1]
            i += 2
        elif args[i] == '--tag' and i + 1 < len(args):
            tag = args[i + 1]
            i += 2
        else:
            i += 1
    
    data = load_data()
    task = {
        'id': str(int(datetime.utcnow().timestamp() * 1000)),
        'title': title,
        'column': column,
        'tag': tag,
        'created': datetime.utcnow().isoformat() + 'Z'
    }
    data['tasks'].append(task)
    add_activity(data, 'Created', title)
    save_data(data)
    print(f"✅ Added: {title} → {column}")

def cmd_list(args):
    """List all tasks: mc list [--column COLUMN]"""
    data = load_data()
    filter_column = None
    
    if '--column' in args and args.index('--column') + 1 < len(args):
        filter_column = args[args.index('--column') + 1]
    
    tasks = data['tasks']
    if filter_column:
        tasks = [t for t in tasks if t['column'] == filter_column]
    
    if not tasks:
        print("No tasks found")
        return
    
    columns = {'recurring': '🔄', 'backlog': '📋', 'inprogress': '⚡', 'review': '✅'}
    
    for task in tasks:
        icon = columns.get(task['column'], '📌')
        tag = f" [{task['tag']}]" if task['tag'] else ""
        print(f"{icon} {task['title']}{tag} (id: {task['id']})")

def cmd_move(args):
    """Move a task: mc move TASK_ID COLUMN"""
    if len(args) < 2:
        print("Usage: mc move TASK_ID COLUMN")
        return
    
    task_id = args[0]
    new_column = args[1]
    
    data = load_data()
    task = next((t for t in data['tasks'] if t['id'] == task_id), None)
    
    if not task:
        print(f"❌ Task not found: {task_id}")
        return
    
    old_column = task['column']
    task['column'] = new_column
    add_activity(data, f'Moved from {old_column} to {new_column}', task['title'])
    save_data(data)
    print(f"✅ Moved: {task['title']} → {new_column}")

def cmd_delete(args):
    """Delete a task: mc delete TASK_ID"""
    if not args:
        print("Usage: mc delete TASK_ID")
        return
    
    task_id = args[0]
    data = load_data()
    task = next((t for t in data['tasks'] if t['id'] == task_id), None)
    
    if not task:
        print(f"❌ Task not found: {task_id}")
        return
    
    data['tasks'] = [t for t in data['tasks'] if t['id'] != task_id]
    add_activity(data, 'Deleted', task['title'])
    save_data(data)
    print(f"✅ Deleted: {task['title']}")

def cmd_help(args):
    """Show help"""
    print("""Mission Control CLI

Usage:
  mc add "Task title" [--column COLUMN] [--tag TAG]
  mc list [--column COLUMN]
  mc move TASK_ID COLUMN
  mc delete TASK_ID
  mc help

Columns: recurring, backlog, inprogress, review
Tags: youtube, newsletter, coding, content

Examples:
  mc add "Research DeepSeek R1" --column backlog --tag coding
  mc list --column backlog
  mc move 123456 inprogress
  mc delete 123456
""")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        cmd_help([])
        sys.exit(0)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    commands = {
        'add': cmd_add,
        'list': cmd_list,
        'ls': cmd_list,
        'move': cmd_move,
        'mv': cmd_move,
        'delete': cmd_delete,
        'rm': cmd_delete,
        'help': cmd_help
    }
    
    if command in commands:
        commands[command](args)
    else:
        print(f"Unknown command: {command}")
        cmd_help([])
