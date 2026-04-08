"""Rate Limiting Agent"""


import time
from collections import deque


class RateLimiter:
    def __init__(self, max_requests: int = 10, window: int = 60):
        self.max = max_requests
        self.window = window
        self.requests = deque()
    
    def allow(self) -> bool:
        now = time.time()
        self.requests = deque([t for t in self.requests if now - t < self.window])
        if len(self.requests) < self.max:
            self.requests.append(now)
            return True
        return False
    
    def wait_time(self) -> float:
        if not self.requests:
            return 0
        return self.window - (time.time() - self.requests[0])


if __name__ == "__main__":
    limiter = RateLimiter(max_requests=3, window=10)
    for i in range(5):
        print(f"Request {i+1}: {'✅' if limiter.allow() else '❌ wait ' + str(limiter.wait_time())[:4] + 's'}")
