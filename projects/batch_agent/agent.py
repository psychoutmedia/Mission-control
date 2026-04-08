"""
Batch Processing Agent
Process multiple tasks in parallel or sequence.

Run with: python batch_agent/agent.py
"""

import concurrent.futures
import time
from dataclasses import dataclass


@dataclass
class BatchResult:
    task_id: str
    success: bool
    result: str
    duration: float


class BatchAgent:
    """Process multiple tasks efficiently."""
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.results: list[BatchResult] = []
    
    def process_task(self, task_id: str, task_fn, *args) -> BatchResult:
        """Process a single task."""
        start = time.time()
        try:
            result = task_fn(*args)
            return BatchResult(task_id, True, str(result), time.time() - start)
        except Exception as e:
            return BatchResult(task_id, False, str(e), time.time() - start)
    
    def run_parallel(self, tasks: list[tuple]) -> list[BatchResult]:
        """Run tasks in parallel."""
        print(f"\n🚀 Running {len(tasks)} tasks in parallel...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self.process_task, tid, tf, *args)
                for tid, tf, *args in tasks
            ]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        self.results = results
        return results
    
    def run_sequential(self, tasks: list[tuple]) -> list[BatchResult]:
        """Run tasks sequentially."""
        print(f"\n� Running {len(tasks)} tasks sequentially...")
        
        results = []
        for tid, tf, *args in tasks:
            result = self.process_task(tid, tf, *args)
            results.append(result)
        
        self.results = results
        return results
    
    def summarize(self) -> dict:
        """Summarize batch results."""
        total = len(self.results)
        success = sum(1 for r in self.results if r.success)
        total_time = sum(r.duration for r in self.results)
        
        return {
            "total": total,
            "success": success,
            "failed": total - success,
            "total_time": total_time,
            "avg_time": total_time / total if total else 0
        }


def task_example(x):
    """Example task."""
    time.sleep(0.5)
    return f"Processed {x} -> {x * 2}"


if __name__ == "__main__":
    agent = BatchAgent(max_workers=3)
    
    tasks = [
        ("task_1", task_example, 1),
        ("task_2", task_example, 2),
        ("task_3", task_example, 3),
    ]
    
    print("="*50)
    print("📦 Batch Processing Agent")
    print("="*50)
    
    # Parallel
    results = agent.run_parallel(tasks)
    summary = agent.summarize()
    
    print(f"\n✅ Results: {summary['success']}/{summary['total']} successful")
    print(f"⏱ Total time: {summary['total_time']:.2f}s")
