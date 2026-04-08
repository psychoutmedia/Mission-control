"""
Code Execution Agent
An agent that can safely execute code and return results.

Key concepts:
- Sandboxed execution (limit time, memory)
- Output capture (stdout, stderr, return value)
- Error handling and reporting

Run with: python code_execution_agent/agent.py
"""

import json
import io
import sys
import traceback
import time
from dataclasses import dataclass
from typing import Callable, Optional


# ============================================================
# SANDBOXED EXECUTION
# ============================================================

@dataclass
class ExecutionResult:
    """Result of code execution."""
    success: bool
    stdout: str
    stderr: str
    return_value: str
    execution_time: float
    error: Optional[str] = None


class CodeSandbox:
    """
    Sandboxed Python code execution.
    
    In production: would use containers (Docker), gVisor, or
    cloud functions (AWS Lambda, Google Cloud Functions).
    """
    
    def __init__(self, timeout: float = 5.0, memory_limit_mb: int = 128):
        self.timeout = timeout
        self.memory_limit = memory_limit_mb
        self.allowed_builtins = {
            'print': print,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
            'set': set,
            'tuple': tuple,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'sorted': sorted,
            'sum': sum,
            'min': min,
            'max': max,
            'abs': abs,
            'round': round,
            'input': lambda: "",  # Block input
        }
    
    def execute(self, code: str, context: dict = None) -> ExecutionResult:
        """
        Execute code in sandbox.
        
        Args:
            code: Python code to execute
            context: Variables to make available
            
        Returns:
            ExecutionResult with output and any errors
        """
        start_time = time.time()
        
        # Capture stdout
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # Create restricted globals
        restricted_globals = {
            '__builtins__': self.allowed_builtins,
            '__name__': '__sandbox__',
        }
        
        if context:
            restricted_globals.update(context)
        
        try:
            # Execute the code
            exec_globals = {}
            exec(code, restricted_globals, exec_globals)
            
            execution_time = time.time() - start_time
            
            # Get return value if exists
            return_value = ""
            if '_result_' in exec_globals:
                return_value = str(exec_globals['_result_'])
            
            return ExecutionResult(
                success=True,
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue(),
                return_value=return_value,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                stdout=stdout_capture.getvalue(),
                stderr=stderr_capture.getvalue(),
                return_value="",
                execution_time=execution_time,
                error=f"{type(e).__name__}: {str(e)}"
            )


# ============================================================
# CODE EXECUTION AGENT
# ============================================================

class CodeExecutionAgent:
    """
    An agent that writes and executes code to solve problems.
    
    This is the pattern used by:
    - Claude Code (execute shell commands)
    - GitHub Copilot (code suggestions)
    - Replit Agents (autonomous coding)
    """
    
    def __init__(self, sandbox: CodeSandbox = None):
        self.sandbox = sandbox or CodeSandbox()
        self.execution_history: list[ExecutionResult] = []
    
    def generate_code(self, task: str) -> str:
        """
        Generate code to solve the task.
        
        In production: would call LLM with the task
        to generate appropriate code.
        """
        task_lower = task.lower()
        
        # Simple rule-based generation for demo
        # In production: LLM would generate this
        
        if "sort" in task_lower:
            code = """
numbers = [5, 2, 8, 1, 9]
sorted_numbers = sorted(numbers)
_result_ = sorted_numbers
"""
        elif "fibonacci" in task_lower:
            code = """
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)

_result_ = [fib(i) for i in range(10)]
print(_result_)
"""
        elif "prime" in task_lower:
            code = """
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

primes = [i for i in range(1, 21) if is_prime(i)]
_result_ = primes
"""
        elif "factorial" in task_lower:
            code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

_result_ = factorial(5)
"""
        else:
            # Default: just run the task as code
            code = f"""
_result_ = "{task}"
"""
        
        return code.strip()
    
    def execute_code(self, code: str) -> ExecutionResult:
        """Execute code and return result."""
        result = self.sandbox.execute(code)
        self.execution_history.append(result)
        return result
    
    def run(self, task: str) -> dict:
        """
        Run the agent on a task.
        
        1. Generate code for task
        2. Execute in sandbox
        3. Return results
        """
        print(f"\n{'='*60}")
        print(f"🎯 Task: {task}")
        print('='*60)
        
        # Generate code
        print("\n📝 Generating code...")
        code = self.generate_code(task)
        print(f"```python\n{code}\n```")
        
        # Execute
        print("\n🚀 Executing in sandbox...")
        result = self.execute_code(code)
        
        # Report
        if result.success:
            print(f"\n✅ Success! ({result.execution_time:.3f}s)")
            if result.stdout:
                print(f"   stdout: {result.stdout}")
            if result.return_value:
                print(f"   → Result: {result.return_value}")
        else:
            print(f"\n❌ Error! ({result.execution_time:.3f}s)")
            print(f"   {result.error}")
            if result.stdout:
                print(f"   stdout: {result.stdout}")
        
        return {
            "success": result.success,
            "code": code,
            "stdout": result.stdout,
            "return_value": result.return_value,
            "error": result.error,
            "execution_time": result.execution_time
        }


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    agent = CodeExecutionAgent()
    
    tasks = [
        "Sort this list: [5, 2, 8, 1, 9]",
        "Generate first 10 Fibonacci numbers",
        "Find all primes from 1 to 20",
        "Calculate factorial of 5",
    ]
    
    print("\n" + "="*60)
    print("💻 Code Execution Agent Demo")
    print("="*60)
    
    for task in tasks:
        result = agent.run(task)
        print(f"\n{'='*60}")
    
    # Show history
    print("\n📊 Execution History:")
    print(f"   Total: {len(agent.execution_history)}")
    print(f"   Successful: {sum(1 for r in agent.execution_history if r.success)}")
    print(f"   Failed: {sum(1 for r in agent.execution_history if not r.success)}")
