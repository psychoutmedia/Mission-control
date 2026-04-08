"""
Evaluation Agent
Tests and evaluates other agents.

Metrics:
- Success rate
- Response time
- Correctness
- Tool use accuracy

Run with: python evaluation_agent/agent.py
"""

import json
import time
from dataclasses import dataclass
from typing import Callable, Any


# ============================================================
# METRICS
# ============================================================

@dataclass
class EvaluationResult:
    """Result of evaluating an agent."""
    task: str
    success: bool
    response_time: float
    correctness: float  # 0-1
    feedback: str


class AgentEvaluator:
    """Evaluates agent performance."""
    
    def __init__(self):
        self.results: list[EvaluationResult] = []
    
    def evaluate(self, agent_fn: Callable, test_cases: list[dict]) -> dict:
        """Run evaluation on test cases."""
        print(f"\n{'='*60}")
        print(f"🧪 Evaluating Agent")
        print(f"{'='*60}")
        
        for tc in test_cases:
            task = tc["input"]
            expected = tc.get("expected", "")
            
            print(f"\n📝 Task: {task}")
            
            start = time.time()
            try:
                result = agent_fn(task)
                response_time = time.time() - start
                
                # Simple correctness check
                if expected and expected.lower() in str(result).lower():
                    correctness = 1.0
                    success = True
                else:
                    correctness = 0.5
                    success = result != "Error"
                
                feedback = "Good" if success else "Needs improvement"
                
            except Exception as e:
                response_time = time.time() - start
                success = False
                correctness = 0.0
                feedback = f"Error: {e}"
            
            eval_result = EvaluationResult(
                task=task,
                success=success,
                response_time=response_time,
                correctness=correctness,
                feedback=feedback
            )
            self.results.append(eval_result)
            
            print(f"   ✅ Success: {success} | Time: {response_time:.2f}s | Correct: {correctness}")
        
        return self._summarize()
    
    def _summarize(self) -> dict:
        """Summarize evaluation results."""
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        avg_time = sum(r.response_time for r in self.results) / total
        avg_correct = sum(r.correctness for r in self.results) / total
        
        summary = {
            "total_tests": total,
            "success_rate": successful / total,
            "avg_response_time": avg_time,
            "avg_correctness": avg_correct
        }
        
        print(f"\n{'='*60}")
        print(f"📊 Summary:")
        print(f"   Success Rate: {summary['success_rate']*100:.1f}%")
        print(f"   Avg Time: {summary['avg_response_time']:.2f}s")
        print(f"   Avg Correctness: {summary['avg_correctness']*100:.1f}%")
        
        return summary


# ============================================================
# DEMO
# ============================================================

def simple_agent(task: str) -> str:
    """Simple test agent."""
    task_lower = task.lower()
    if "weather" in task_lower:
        return "The weather is sunny."
    elif "time" in task_lower:
        return "The time is 2pm."
    else:
        return "I don't know."


if __name__ == "__main__":
    evaluator = AgentEvaluator()
    
    test_cases = [
        {"input": "What's the weather?", "expected": "weather"},
        {"input": "What time is it?", "expected": "time"},
        {"input": "Tell me a fact", "expected": ""},
    ]
    
    results = evaluator.evaluate(simple_agent, test_cases)
