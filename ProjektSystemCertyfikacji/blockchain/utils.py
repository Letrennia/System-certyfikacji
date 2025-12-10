# utils.py
import json
from typing import Any, Dict

def pretty_json(data: Any) -> str:
    """Zwraca ładnie sformatowany JSON — do logów i debugowania."""
    return json.dumps(data, indent=4, ensure_ascii=False)

def is_valid_hash(hash_str: str) -> bool:
    """Sprawdza czy string wygląda na poprawny SHA-256."""
    if not isinstance(hash_str, str):
        return False
    return len(hash_str) == 64 and all(c in "0123456789abcdef" for c in hash_str.lower())

def sanitize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Konwertuje obiekty Django / daty do json-friendly formatu."""
    sanitized = {}
    for key, value in data.items():
        if hasattr(value, "isoformat"):
            sanitized[key] = value.isoformat()
        else:
            sanitized[key] = value
    return sanitized
