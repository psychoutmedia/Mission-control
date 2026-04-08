"""Config Agent"""
import json

class Config:
    def __init__(self, data=None):
        self.data = data or {}
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def set(self, key, value):
        self.data[key] = value
    
    def save(self, path):
        with open(path, 'w') as f:
            json.dump(self.data, f)

c = Config({"model": "phi3", "temp": 0.7})
print(f"Model: {c.get('model')}")
c.set("max_tokens", 1000)
c.save("/tmp/config.json")
print("✅ Config saved")
