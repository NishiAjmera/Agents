import json
from typing import List, Dict

MEMORY_FILE = "memory.json"


def read_memory() -> List[Dict]:
    """Reads the conversation history from the memory file."""
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def write_memory(history: List[Dict]):
    """Writes the conversation history to the memory file."""
    with open(MEMORY_FILE, "w") as f:
        json.dump(history, f, indent=2)
