"""
Feedback Loop Agent
Human-in-the-loop pattern for agent oversight.

Pattern:
- Agent takes action
- Human reviews/approves
- Agent continues or corrects

Run with: python feedback_agent/agent.py
"""

import json
from dataclasses import dataclass
from enum import Enum


class FeedbackType(Enum):
    APPROVE = "approve"
    REJECT = "reject"
    MODIFY = "modify"


@dataclass
class Action:
    """An action proposed by the agent."""
    id: str
    description: str
    tool: str
    params: dict
    status: str = "pending"  # pending, approved, rejected, executed


class HumanInTheLoopAgent:
    """
    Agent that asks for human feedback before executing sensitive actions.
    """
    
    def __init__(self, name: str = "Agent"):
        self.name = name
        self.pending_actions: list[Action] = []
        self.executed_actions: list[Action] = []
        self.auto_approve = True  # Set to False for human approval
    
    def propose_action(self, description: str, tool: str, params: dict) -> Action:
        """Propose an action for human review."""
        action = Action(
            id=f"action_{len(self.pending_actions) + 1}",
            description=description,
            tool=tool,
            params=params
        )
        self.pending_actions.append(action)
        
        if self.auto_approve:
            self.approve_action(action.id)
        
        return action
    
    def approve_action(self, action_id: str) -> bool:
        """Human approves an action."""
        for action in self.pending_actions:
            if action.id == action_id:
                action.status = "approved"
                self.execute_action(action)
                return True
        return False
    
    def reject_action(self, action_id: str, reason: str = "") -> bool:
        """Human rejects an action."""
        for action in self.pending_actions:
            if action.id == action_id:
                action.status = "rejected"
                print(f"❌ Rejected: {action.description} - {reason}")
                return True
        return False
    
    def modify_action(self, action_id: str, new_params: dict) -> bool:
        """Human modifies an action."""
        for action in self.pending_actions:
            if action.id == action_id:
                action.params.update(new_params)
                print(f"✏️ Modified: {action.description}")
                return True
        return False
    
    def execute_action(self, action: Action):
        """Execute an approved action."""
        print(f"🔧 Executing: {action.description}")
        # In production: actually call the tool
        action.status = "executed"
        self.executed_actions.append(action)
    
    def get_pending(self) -> list[Action]:
        """Get all pending actions."""
        return [a for a in self.pending_actions if a.status == "pending"]


if __name__ == "__main__":
    agent = HumanInTheLoopAgent(name="Assistant")
    
    print("="*50)
    print("🔄 Feedback Loop Agent Demo")
    print("="*50)
    
    # Propose some actions
    agent.propose_action("Send email to customer", "send_email", {"to": "user@example.com"})
    agent.propose_action("Delete file", "delete_file", {"path": "/tmp/test.txt"})
    agent.propose_action("Search for information", "search", {"query": "Python"})
    
    print(f"\n📋 Pending actions: {len(agent.get_pending())}")
    
    # Human reviews
    for action in agent.get_pending():
        print(f"  - {action.description} ({action.tool})")
    
    # Approve some, reject some
    agent.approve_action("action_1")
    agent.reject_action("action_2", "Too risky")
    agent.approve_action("action_3")
    
    print(f"\n✅ Executed: {len(agent.executed_actions)}")
