"""
Tool-Use Agent with Real APIs
An agent that uses real external APIs for weather, search, etc.

APIs used:
- Open-Meteo (free weather API)
- DuckDuckGo (free search)

Run with: python tool_use_agent/agent.py
"""

import json
import sys
import requests
import re
sys.path.insert(0, '/Users/marksstephenson/clawd/projects/ollama_extensions')
from client import OllamaClient


# ============================================================
# REAL TOOLS
# ============================================================

def get_weather(city: str) -> str:
    """Get real weather from Open-Meteo API."""
    # First geocode the city
    try:
        # Use Open-Meteo geocoding
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_resp = requests.get(geo_url, timeout=10).json()
        
        if not geo_resp.get("results"):
            return json.dumps({"error": f"City not found: {city}"})
        
        lat = geo_resp["results"][0]["latitude"]
        lon = geo_resp["results"][0]["longitude"]
        city_name = geo_resp["results"][0]["name"]
        
        # Get weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_resp = requests.get(weather_url, timeout=10).json()
        
        if "current_weather" in weather_resp:
            cw = weather_resp["current_weather"]
            return json.dumps({
                "city": city_name,
                "temperature": cw["temperature"],
                "windspeed": cw["windspeed"],
                "condition": "Clear" if cw["weathercode"] == 0 else "Cloudy"
            })
        
        return json.dumps({"error": "Weather data unavailable"})
    
    except Exception as e:
        return json.dumps({"error": str(e)})


def search_web(query: str) -> str:
    """Real web search using DuckDuckGo."""
    try:
        url = "https://api.duckduckgo.com/"
        params = {"q": query, "format": "json", "no_html": 1}
        resp = requests.get(url, params=params, timeout=10).json()
        
        if resp.get("AbstractText"):
            return json.dumps({
                "result": resp["AbstractText"],
                "source": resp.get("AbstractSource", "Web")
            })
        
        # Try related topics
        if resp.get("RelatedTopics"):
            topic = resp["RelatedTopics"][0]
            return json.dumps({
                "result": topic.get("Text", "No results"),
                "source": "Web"
            })
        
        return json.dumps({"result": f"No results for: {query}"})
    
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_time(city: str) -> str:
    """Get current time for a city using WorldTimeAPI."""
    try:
        # Map cities to timezone
        tz_map = {
            "london": "Europe/London",
            "new york": "America/New_York",
            "tokyo": "Asia/Tokyo",
            "san francisco": "America/Los_Angeles",
            "paris": "Europe/Paris",
            "sydney": "Australia/Sydney",
        }
        
        tz = tz_map.get(city.lower(), "UTC")
        url = f"http://worldtimeapi.org/api/timezone/{tz}"
        resp = requests.get(url, timeout=10).json()
        
        if "datetime" in resp:
            dt = resp["datetime"][:19].replace("T", " ")
            return json.dumps({"city": city, "time": dt, "timezone": tz})
        
        return json.dumps({"error": "Time unavailable"})
    
    except Exception as e:
        return json.dumps({"error": str(e)})


TOOLS = {
    "get_weather": {
        "func": get_weather,
        "description": "Get current weather for a city. Input: city name."
    },
    "search_web": {
        "func": search_web,
        "description": "Search the web for information. Input: search query."
    },
    "get_time": {
        "func": get_time,
        "description": "Get current time for a city. Input: city name."
    },
}


# ============================================================
# TOOL-USE AGENT
# ============================================================

class ToolUseAgent:
    """
    An agent that uses real external tools/APIs.
    
    Key difference from simulated tools:
    - Real network calls
    - Error handling for API failures
    - Rate limiting awareness
    """
    
    def __init__(self, model: str = "phi3", client: OllamaClient = None):
        self.model = model
        self.client = client or OllamaClient()
        self.tools = TOOLS
        self.max_steps = 4
    
    def _build_prompt(self, question: str) -> list[dict]:
        """Build prompt with tool definitions."""
        tool_desc = "\n".join(
            f"- {name}: {info['description']}"
            for name, info in self.tools.items()
        )
        
        system = f"""You are a helpful assistant with access to real tools.

Available tools:
{tool_desc}

Instructions:
- Use tools to get real, up-to-date information
- After using a tool, explain what you learned
- Provide your final answer based on tool results

Format:
Thought: [what to do]
Action: [tool_name]
Action Input: [input]
[tool result]
Thought: [analysis]
Final Answer: [your answer]"""
        
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": question}
        ]
    
    def _parse_response(self, response: str) -> tuple[str, str, str, bool]:
        """Parse LLM response."""
        # Extract action
        action_match = re.search(r"Action:\s*(\w+)", response)
        action = action_match.group(1).strip() if action_match else ""
        
        # Extract input
        input_match = re.search(r"Action Input:\s*(.+?)(?:\n|$)", response)
        action_input = input_match.group(1).strip() if input_match else ""
        
        # Check for final
        final_match = re.search(r"Final Answer:\s*(.+)", response, re.DOTALL)
        final = final_match.group(1).strip() if final_match else None
        
        thought_match = re.search(r"Thought:\s*(.+?)(?:Action:|$)", response, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else ""
        
        return thought, action, action_input, final
    
    def _execute_tool(self, action: str, input_data: str) -> str:
        """Execute a tool."""
        if action not in self.tools:
            return f"Error: Unknown tool '{action}'"
        
        try:
            func = self.tools[action]["func"]
            result = func(input_data)
            return result
        except Exception as e:
            return f"Error: {e}"
    
    def run(self, question: str) -> str:
        """Run the agent."""
        print(f"\n{'='*60}")
        print(f"❓ Question: {question}")
        print('='*60)
        
        messages = self._build_prompt(question)
        
        for step in range(self.max_steps):
            # Get response
            try:
                resp = self.client.chat(self.model, messages, stream=False)
                response = resp.get("message", {}).get("content", "")
            except Exception as e:
                print(f"❌ Error: {e}")
                break
            
            # Parse
            thought, action, action_input, final = self._parse_response(response)
            
            print(f"\n📍 Step {step + 1}")
            if thought:
                print(f"   💭 {thought[:80]}...")
            
            if final:
                print(f"\n✅ Final Answer: {final}")
                return final
            
            if action:
                print(f"   🔧 Using: {action}")
                print(f"   📥 Input: {action_input}")
                
                # Execute
                result = self._execute_tool(action, action_input)
                print(f"   📤 Result: {result[:150]}...")
                
                # Add result to conversation
                messages.append({"role": "assistant", "content": response})
                messages.append({
                    "role": "user",
                    "content": f"Tool result: {result}\n\nWhat's your next thought or final answer?"
                })
        
        return "Max steps reached"


# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    client = OllamaClient()
    
    if not client.is_available():
        print("❌ Ollama not running. Start with: ollama serve")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🌐 Tool-Use Agent with Real APIs")
    print("="*60)
    
    agent = ToolUseAgent(model="phi3")
    
    questions = [
        "What's the weather in London?",
        "What time is it in Tokyo?",
    ]
    
    for q in questions:
        result = agent.run(q)
        print(f"\n{'='*60}")
