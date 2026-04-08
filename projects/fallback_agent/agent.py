"""Fallback Agent"""
class FallbackAgent:
    def __init__(self):
        self.models = ["gpt-4", "gpt-3.5", "local"]
    
    def run(self, prompt):
        for model in self.models:
            try:
                print(f"Try: {model}")
                if model == "local":
                    return f"Success with {model}"
                raise Exception("API fail")
            except:
                continue
        return "All failed"

if __name__ == "__main__":
    a = FallbackAgent()
    print(a.run("test"))
