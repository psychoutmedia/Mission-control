"""Logging Agent"""
import json
import time

class Logger:
    def __init__(self):
        self.logs = []
    
    def log(self, level: str, msg: str):
        self.logs.append({"time": time.time(), "level": level, "msg": msg})
        print(f"[{level}] {msg}")
    
    def get_logs(self, level: str = None):
        return [l for l in self.logs if not level or l["level"] == level]

if __name__ == "__main__":
    logger = Logger()
    logger.log("INFO", "Agent started")
    logger.log("ERROR", "Something failed")
    logger.log("INFO", "Retrying...")
    print(f"\nAll logs: {len(logger.get_logs())}")
    print(f"Errors: {len(logger.get_logs('ERROR'))}")
