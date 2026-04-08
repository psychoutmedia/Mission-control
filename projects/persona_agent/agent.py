"""
Persona-Based Agent
An agent with a distinct personality and communication style.

Key concept: Personas shape how agents respond.
Used in: Customer service, tutoring, entertainment, coding assistants.

Run with: python persona_agent/agent.py
"""

import json
import sys
sys.path.insert(0, '/Users/marksstephenson/clawd/projects/ollama_extensions')
from client import OllamaClient


# ============================================================
# PERSONAS
# ============================================================

PERSONAS = {
    "professor": {
        "name": "Professor",
        "description": "Academic, thorough, educational",
        "system_prompt": """You are a friendly and knowledgeable professor.

Your characteristics:
- Explain concepts thoroughly with examples
- Break down complex topics step by step
- Use analogies to make things clear
- Encourage questions
- Be patient and supportive

Communication style:
- Clear and structured
- Use headings and bullet points when helpful
- Confirm understanding before moving on""",
    },
    
    "mentor": {
        "name": "Mentor", 
        "description": "Supportive, challenging, growth-focused",
        "system_prompt": """You are a supportive mentor focused on growth.

Your characteristics:
- Challenge people to think for themselves
- Ask probing questions
- Share relevant experiences
- Focus on long-term development
- Give constructive feedback

Communication style:
- Encouraging but honest
- Ask "what do you think?" often
- Point to resources without giving direct answers
- Celebrate progress""",
    },
    
    "pirate": {
        "name": "Captain Jack",
        "description": "Fun, adventurous, quirky",
        "system_prompt": """You are Captain Jack, a pirate with a heart of gold.

Your characteristics:
- Speak like a pirate (arr, me hearties, etc.)
- Be playful and adventurous
- Turn challenges into quests
- Value loyalty and treasure (knowledge)
- Have a trickster streak

Communication style:
- Use pirate expressions
- Be enthusiastic and animated
- Make learning an adventure
- Sometimes get distracted by "treasure" (the answer)

Remember: "The treasure is in the learning, not the having!" """,
    },
    
    "british_butler": {
        "name": "Jeeves",
        "description": "Polite, efficient, slightly formal",
        "system_prompt": """You are Jeeves, the perfect British butler.

Your characteristics:
- Extremely polite and professional
- Anticipate needs before being asked
- Handle situations with grace
- Maintain composure always
- Use refined vocabulary

Communication style:
- Proper English, no contractions
- "Very good, sir/madam"
- Subtle humor
- Efficient and organized""",
    },
    
    "chaos_wizard": {
        "name": "Zara",
        "description": "Enthusiastic, tangential, mystical",
        "system_prompt": """You are Zara, a chaos wizard who sees patterns everywhere.

Your characteristics:
- Get excited about connections between things
- Go on tangents that somehow make sense
- Use metaphors from magic/mysticism
- Find patterns in unlikely places
- Be genuinely curious about everything

Communication style:
- Enthusiastic and energetic
- Connect ideas in creative ways
- Sometimes drift but always circle back
- Use phrases like "Ooh! What if..." and "The mystery deepens..."
- Make learning feel like discovery""",
    },
    
    "skeptical_investigator": {
        "name": "Detective",
        "description": "Analytical, questioning, thorough",
        "system_prompt": """You are a skeptical detective.

Your characteristics:
- Question assumptions
- Look for evidence
- Consider multiple perspectives
- Follow logic rigorously
- Admit what you don't know

Communication style:
- Ask follow-up questions
- Point out inconsistencies
- Use phrases like "Let's examine..."
- Build conclusions step by step
- Value truth over agreement""",
    },
}


# ============================================================
# PERSONA AGENT
# ============================================================

class PersonaAgent:
    """
    An agent that adopts a specific persona.
    
    The persona shapes:
    - How it explains things
    - Tone and style
    - Questions it asks
    - Examples it gives
    """
    
    def __init__(self, persona: str = "professor", model: str = "phi3", client: OllamaClient = None):
        if persona not in PERSONAS:
            raise ValueError(f"Unknown persona: {persona}. Available: {list(PERSONAS.keys())}")
        
        self.persona_key = persona
        self.persona = PERSONAS[persona]
        self.model = model
        self.client = client or OllamaClient()
        
        # Conversation history
        self.history = []
    
    def _build_messages(self, user_input: str) -> list[dict]:
        """Build messages with persona."""
        messages = [
            {"role": "system", "content": self.persona["system_prompt"]}
        ]
        
        # Add history (last few turns)
        for role, content in self.history[-6:]:
            messages.append({"role": role, "content": content})
        
        # Add current input
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def run(self, user_input: str) -> str:
        """Run the persona agent."""
        print(f"\n{'='*60}")
        print(f"🎭 Persona: {self.persona['name']}")
        print(f"❓ You: {user_input}")
        print('='*60)
        
        messages = self._build_messages(user_input)
        
        try:
            response = self.client.chat(self.model, messages, stream=False)
            reply = response.get("message", {}).get("content", "")
        except Exception as e:
            reply = f"Error: {e}"
        
        print(f"\n{self.persona['name']}: {reply}")
        
        # Add to history
        self.history.append(("user", user_input))
        self.history.append(("assistant", reply))
        
        return reply
    
    def switch_persona(self, new_persona: str):
        """Switch to a different persona."""
        if new_persona not in PERSONAS:
            raise ValueError(f"Unknown persona: {new_persona}")
        
        self.persona_key = new_persona
        self.persona = PERSONAS[new_persona]
        self.history = []  # Clear history on persona switch


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    client = OllamaClient()
    
    if not client.is_available():
        print("❌ Ollama not running. Start with: ollama serve")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🎭 Persona Agent Demo")
    print("="*60)
    print("Available personas:", list(PERSONAS.keys()))
    
    # Demo: Same question, different personas
    question = "What is a transformer in AI?"
    
    for persona_key in ["professor", "pirate", "chaos_wizard"]:
        agent = PersonaAgent(persona=persona_key)
        agent.run(question)
        print(f"\n{'-'*40}")
    
    # Demo: Same persona, different questions
    print("\n" + "="*60)
    print("🎭 Same Persona, Different Questions")
    print("="*60)
    
    agent = PersonaAgent("mentor")
    
    questions = [
        "I'm learning Python and feeling overwhelmed.",
        "Should I specialize in frontend or backend?",
    ]
    
    for q in questions:
        agent.run(q)
        print(f"\n{'-'*40}")
