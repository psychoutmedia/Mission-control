"""
Chain-of-Thought (CoT) Agent
An agent that explicitly shows its reasoning step by step.

Key insight: Making reasoning explicit improves accuracy on complex tasks.
This is why "Let's think step by step" works so well.

Run with: python cot_agent/agent.py
"""

import json
import re
import sys
sys.path.insert(0, '/Users/marksstephenson/clawd/projects/ollama_extensions')
from client import OllamaClient


# ============================================================
# COT AGENT
# ============================================================

class ChainOfThoughtAgent:
    """
    An agent that explicitly shows its reasoning.
    
    Key differences from ReAct:
    - Focus on reasoning, not tools
    - Step-by-step logical deduction
    - Can self-correct reasoning
    
    Used in: GPT-4, Claude, Gemini
    """
    
    def __init__(self, model: str = "phi3", client: OllamaClient = None):
        self.model = model
        self.client = client or OllamaClient()
        self.reasoning_history = []
    
    def _build_prompt(self, question: str, include_examples: bool = True) -> list[dict]:
        """Build prompt with CoT instructions."""
        
        if include_examples:
            system = """You are a logical reasoning assistant. Think step by step.

When solving problems:
1. Break down the problem into smaller parts
2. Show your work for each step
3. Verify your reasoning at each step
4. Combine parts to get the final answer

Format your response like this:
Step 1: [what you're doing]
Reasoning: [why you're doing this]
Step 2: [next step]
...
Conclusion: [final answer]"""
        else:
            system = """Think step by step about this problem. Show your reasoning clearly."""
        
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": question}
        ]
    
    def _parse_reasoning(self, response: str) -> dict:
        """Extract reasoning steps from response."""
        steps = []
        conclusion = ""
        
        # Find all steps
        step_matches = re.findall(
            r"Step \d+:([^\n]+)\n*Reasoning:([^\n]+)",
            response,
            re.IGNORECASE
        )
        
        for step_num, step_content in step_matches:
            steps.append({
                "step": step_num.strip(),
                "reasoning": step_content.strip()
            })
        
        # Find conclusion
        conc_match = re.search(r"Conclusion:([^\n]+)", response, re.IGNORECASE)
        if conc_match:
            conclusion = conc_match.group(1).strip()
        
        return {
            "steps": steps,
            "conclusion": conclusion or response[-200:],
            "raw": response
        }
    
    def run(self, question: str, show_reasoning: bool = True) -> dict:
        """Run CoT agent on a question."""
        print(f"\n{'='*60}")
        print(f"❓ Question: {question}")
        print('='*60)
        
        # Build prompt
        messages = self._build_prompt(question)
        
        # Get response
        try:
            response = self.client.chat(self.model, messages, stream=False)
            response_text = response.get("message", {}).get("content", "")
        except Exception as e:
            return {"error": str(e)}
        
        # Parse reasoning
        parsed = self._parse_reasoning(response_text)
        
        if show_reasoning:
            print(f"\n🧠 Reasoning:")
            for i, step in enumerate(parsed["steps"], 1):
                print(f"   {i}. {step['step']}")
                print(f"      → {step['reasoning']}")
            
            if parsed["conclusion"]:
                print(f"\n✅ Conclusion: {parsed['conclusion']}")
        
        return {
            "question": question,
            "reasoning": parsed["steps"],
            "conclusion": parsed["conclusion"],
            "raw": parsed["raw"]
        }


# ============================================================
# MATH COT EXAMPLE
# ============================================================

class MathCoTAgent:
    """
    Specialized CoT for math problems.
    
    Shows: problem decomposition → calculation → verification
    """
    
    def __init__(self, model: str = "phi3", client: OllamaClient = None):
        self.model = model
        self.client = client or OllamaClient()
    
    def _build_math_prompt(self, problem: str) -> list[dict]:
        """Build prompt for math CoT."""
        system = """You are an expert math tutor. Solve this problem step by step.

For math problems:
1. Identify what's being asked
2. Identify known values
3. Select the right approach
4. Show each calculation
5. Verify the answer

Use this format:
Problem: [restate the problem]
Known: [what we know]
Approach: [how we'll solve it]
Calculation: [show your work]
Check: [verify answer]
Answer: [final answer]"""
        
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": problem}
        ]
    
    def run(self, problem: str) -> dict:
        """Solve math problem with CoT."""
        print(f"\n{'='*60}")
        print(f"🔢 Math Problem: {problem}")
        print('='*60)
        
        messages = self._build_math_prompt(problem)
        
        try:
            response = self.client.chat(self.model, messages, stream=False)
            result = response.get("message", {}).get("content", "")
            print(f"\n📝 Solution:\n{result}")
            return {"problem": problem, "solution": result}
        except Exception as e:
            return {"error": str(e)}


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    client = OllamaClient()
    
    if not client.is_available():
        print("❌ Ollama not running. Start with: ollama serve")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🧠 Chain-of-Thought Agent Demo")
    print("="*60)
    
    # General CoT
    cot = ChainOfThoughtAgent(model="phi3")
    
    questions = [
        "If a train travels 120km in 2 hours, and another train travels 180km in 3 hours, which is faster?",
        "What is the square root of 144?",
    ]
    
    for q in questions:
        result = cot.run(q)
        print(f"\n{'='*60}")
    
    # Math CoT
    print("\n" + "="*60)
    print("🔢 Math CoT Agent")
    print("="*60)
    
    math_agent = MathCoTAgent(model="phi3")
    math_result = math_agent.run("A store has a 20% discount on $50 item. What's the final price?")
