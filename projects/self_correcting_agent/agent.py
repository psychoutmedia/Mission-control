"""
Self-Correcting Agent
An agent that detects errors and automatically fixes them.

Key patterns:
1. Error detection - identify when something went wrong
2. Root cause analysis - understand WHY it failed
3. Fix generation - create a corrected approach
4. Verification - confirm the fix worked

Run with: python self_correcting_agent/agent.py
"""

import json
import re
from dataclasses import dataclass
from typing import Callable, Optional


# ============================================================
# TOOLS WITH INTENTIONAL BUGS (for demo)
# ============================================================

def buggy_calculator(expression: str) -> str:
    """
    Calculator with a bug: doesn't handle parentheses correctly.
    (intentionally buggy for demo)
    """
    try:
        # Bug: using eval directly but it works, so let's add a fake bug
        # Actually for demo, let's make it fail on specific inputs
        if "42" in expression:
            return json.dumps({"error": "Forbidden number detected"})
        result = eval(expression)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})


def search_knowledge(query: str) -> str:
    """Simple search - might not find everything."""
    knowledge = {
        "python": "Python created by Guido van Rossum in 1991.",
        "transformer": "Attention Is All You Need (Vaswani et al., 2017).",
        "llm": "Large Language Model - neural network trained on text.",
    }
    query_lower = query.lower()
    for key, value in knowledge.items():
        if key in query_lower:
            return json.dumps({"result": value})
    return json.dumps({"result": "No results found"})


def validate_email(email: str) -> str:
    """Validate email format."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if re.match(pattern, email):
        return json.dumps({"valid": True, "email": email})
    return json.dumps({"valid": False, "error": "Invalid email format"})


# Tools registry
TOOLS = {
    "calculator": {
        "func": buggy_calculator,
        "description": "Evaluate math expressions.",
        "error_patterns": ["Forbidden number", "error"]
    },
    "search": {
        "func": search_knowledge,
        "description": "Search for information.",
        "error_patterns": ["No results"]
    },
    "validate_email": {
        "func": validate_email,
        "description": "Validate email format.",
        "error_patterns": ["Invalid"]
    },
}


# ============================================================
# ERROR DETECTION & CORRECTION
# ============================================================

@dataclass
class Error:
    """Represents a detected error."""
    tool: str
    input_data: str
    error_message: str
    severity: str  # "critical", "warning", "info"


@dataclass
class Correction:
    """Represents a fix for an error."""
    original_error: Error
    fix_description: str
    new_approach: str
    success: bool = False


class ErrorDetector:
    """Detects errors in tool outputs."""
    
    @staticmethod
    def detect(tool_name: str, output: str) -> Optional[Error]:
        """Detect if output contains an error."""
        tool_info = TOOLS.get(tool_name, {})
        error_patterns = tool_info.get("error_patterns", ["error"])
        
        output_lower = output.lower()
        for pattern in error_patterns:
            if pattern.lower() in output_lower:
                return Error(
                    tool=tool_name,
                    input_data="",
                    error_message=output,
                    severity="critical" if "error" in output_lower else "warning"
                )
        return None


class FixGenerator:
    """Generates fixes for detected errors."""
    
    @staticmethod
    def generate(error: Error, task: str) -> Correction:
        """Generate a fix for the error."""
        tool = error.tool
        
        # Calculator fix: avoid forbidden numbers, simplify
        if tool == "calculator":
            if "forbidden" in error.error_message.lower():
                return Correction(
                    original_error=error,
                    fix_description="Avoid using '42' in calculations",
                    new_approach="Use alternative numbers or operations"
                )
            return Correction(
                original_error=error,
                fix_description="Simplify the expression",
                new_approach="Break down into smaller parts"
            )
        
        # Search fix: try different keywords
        if tool == "search":
            return Correction(
                original_error=error,
                fix_description="Try different search terms",
                new_approach="Use synonyms or broader terms"
            )
        
        # Email validation fix
        if tool == "validate_email":
            return Correction(
                original_error=error,
                fix_description="Check email format",
                new_approach="Ensure email matches pattern: user@domain.com"
            )
        
        # Default
        return Correction(
            original_error=error,
            fix_description="Retry with different approach",
            new_approach="Start fresh with modified input"
        )


# ============================================================
# SELF-CORRECTING AGENT
# ============================================================

class SelfCorrectingAgent:
    """
    An agent that detects errors and fixes them automatically.
    
    Cycle:
    1. Execute - Run the tool
    2. Detect - Check for errors
    3. Analyze - Understand root cause
    4. Fix - Generate corrected approach
    5. Retry - Attempt with fix
    6. Verify - Confirm success
    """
    
    def __init__(self, tools: dict, max_retries: int = 3):
        self.tools = tools
        self.max_retries = max_retries
        self.error_log: list[Error] = []
        self.corrections: list[Correction] = []
    
    def _execute(self, tool_name: str, input_data: str) -> str:
        """Execute a tool."""
        if tool_name not in self.tools:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})
        
        try:
            func = self.tools[tool_name]["func"]
            return func(input_data)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _verify_success(self, output: str) -> bool:
        """Verify the output is successful."""
        try:
            data = json.loads(output)
            if "error" in data:
                return False
            return True
        except:
            return "error" not in output.lower()
    
    def run(self, task: str, tool_name: str, input_data: str) -> dict:
        """Run the self-correcting agent."""
        print(f"\n{'='*60}")
        print(f"🎯 Task: {task}")
        print(f"🔧 Tool: {tool_name}")
        print(f"📥 Input: {input_data}")
        print('='*60)
        
        attempt = 0
        current_input = input_data
        
        while attempt < self.max_retries:
            attempt += 1
            print(f"\n🔄 Attempt {attempt}/{self.max_retries}")
            
            # Execute
            output = self._execute(tool_name, current_input)
            print(f"   Output: {output[:80]}...")
            
            # Detect errors
            error = ErrorDetector.detect(tool_name, output)
            
            if error:
                error.input_data = current_input
                self.error_log.append(error)
                print(f"   ❌ Error detected: {error.error_message[:50]}...")
                
                # Generate fix
                correction = FixGenerator.generate(error, task)
                print(f"   🔧 Fix: {correction.fix_description}")
                print(f"   → New approach: {correction.new_approach}")
                
                self.corrections.append(correction)
                
                # Modify input for retry
                if tool_name == "calculator" and "42" in current_input:
                    # Workaround for the bug
                    current_input = current_input.replace("42", "40+2")
                    print(f"   ↻ Modified input: {current_input}")
                else:
                    # For other cases, just retry with same (for demo)
                    pass
            else:
                print(f"   ✅ Success!")
                return {
                    "success": True,
                    "output": output,
                    "attempts": attempt,
                    "errors_fixed": len(self.error_log)
                }
        
        print(f"\n❌ Failed after {self.max_retries} attempts")
        return {
            "success": False,
            "output": output,
            "attempts": attempt,
            "errors_fixed": len(self.error_log)
        }


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    agent = SelfCorrectingAgent(TOOLS)
    
    print("\n" + "="*60)
    print("🔧 Self-Correcting Agent Demo")
    print("="*60)
    
    # Test 1: Calculator with forbidden number
    result1 = agent.run(
        task="Calculate 15 * 8 + 42",
        tool_name="calculator",
        input_data="15 * 8 + 42"
    )
    
    print(f"\n📊 Result: {result1}")
    
    # Test 2: Search with no results
    result2 = agent.run(
        task="Find information about quantum computing",
        tool_name="search",
        input_data="quantum computing"
    )
    
    print(f"\n📊 Result: {result2}")
    
    # Summary
    print("\n" + "="*60)
    print("📈 Summary")
    print("="*60)
    print(f"Total errors detected: {len(agent.error_log)}")
    print(f"Total corrections attempted: {len(agent.corrections)}")
