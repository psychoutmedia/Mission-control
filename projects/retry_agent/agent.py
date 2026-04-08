"""Retry Logic Agent"""


import time
import random


class RetryAgent:
    def __init__(self, max_retries: int = 3, backoff: float = 1.0):
        self.max = max_retries
        self.backoff = backoff
    
    def run(self, fn, *args, **kwargs):
        for attempt in range(self.max + 1):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                if attempt < self.max:
                    wait = self.backoff * (2 ** attempt)
                    print(f"⚠️ Attempt {attempt+1} failed: {e}. Retrying in {wait:.1f}s...")
                    time.sleep(wait)
                else:
                    raise


def unstable_api():
    if random.random() < 0.6:
        raise Exception("API Error")
    return "✅ Success!"


if __name__ == "__main__":
    retry = RetryAgent(max_retries=3, backoff=0.5)
    try:
        result = retry.run(unstable_api)
        print(result)
    except Exception as e:
        print(f"❌ Failed after retries: {e}")
