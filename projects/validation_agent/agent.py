"""Validation Agent"""
import json

class Validator:
    @staticmethod
    def validate_json(data: str) -> dict:
        try:
            return {"valid": True, "data": json.loads(data)}
        except:
            return {"valid": False, "error": "Invalid JSON"}
    
    @staticmethod
    def validate_email(email: str) -> bool:
        import re
        return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email))
    
    @staticmethod
    def validate_schema(data: dict, schema: dict) -> bool:
        for key in schema.get("required", []):
            if key not in data:
                return False
        return True

if __name__ == "__main__":
    v = Validator()
    print("JSON:", v.validate_json('{"a": 1}'))
    print("Email:", v.validate_email("test@example.com"))
    print("Schema:", v.validate_schema({"name": "test"}, {"required": ["name"]}))
