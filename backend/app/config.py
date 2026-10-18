from typing import Dict

# LLM and app configuration
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2"

MINIMAL_SYSTEM_PROMPT = """
You convert structured inventory issues into formatted action cards.
Do not compute, infer, modify, or add any data. Do not change priorities
or ranking. Do not decide action types. Only translate the provided
input into the exact JSON schema requested.
Return JSON only.
"""

# Safety and stability constants
CAP_DAYS_OF_STOCK = 9999.0
DEFAULT_TIME_WINDOW = 14

# Decision taxonomy mapping and allowed action types
DECISION_TAXONOMY = {
    "stockout_risk": "reorder",
    "overstock": "discount",
    "dead_stock": "clear_inventory",
    "demand_spike": "restock",
}

ALLOWED_ACTION_TYPES = {"reorder", "discount", "clear_inventory", "restock", "monitor"}
