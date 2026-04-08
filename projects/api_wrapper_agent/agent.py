"""
API Wrapper Agent
REST API integration for external services.

Run with: python api_wrapper_agent/agent.py
"""

import requests
import json


class APIWrapper:
    """Wrapper for external APIs."""
    
    def __init__(self, base_url: str = ""):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get(self, endpoint: str, params: dict = None) -> dict:
        """GET request."""
        url = f"{self.base_url}{endpoint}"
        resp = self.session.get(url, params=params)
        return resp.json()
    
    def post(self, endpoint: str, data: dict = None) -> dict:
        """POST request."""
        url = f"{self.base_url}{endpoint}"
        resp = self.session.post(url, json=data)
        return resp.json()


class AgentAPI:
    """Example API wrappers for common services."""
    
    @staticmethod
    def weather(city: str) -> dict:
        """Get weather from Open-Meteo."""
        geo = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        ).json()
        
        if not geo.get("results"):
            return {"error": "City not found"}
        
        lat, lon = geo["results"][0]["latitude"], geo["results"][0]["longitude"]
        
        weather = requests.get(
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        ).json()
        
        return weather.get("current_weather", {})
    
    @staticmethod
    def news(topic: str = "technology") -> list:
        """Get news (mock)."""
        return [
            {"title": f"News about {topic} 1", "source": "News"},
            {"title": f"News about {topic} 2", "source": "News"},
        ]


if __name__ == "__main__":
    print("="*50)
    print("🌐 API Wrapper Agent Demo")
    print("="*50)
    
    # Weather
    weather = AgentAPI.weather("London")
    print(f"\n🌤️ London: {weather}")
    
    # News
    news = AgentAPI.news("AI")
    print(f"\n📰 AI News: {len(news)} articles")
