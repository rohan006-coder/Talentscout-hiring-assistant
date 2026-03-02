import os
import json
import hashlib
from typing import Dict, Any

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def hash_contact(email: str | None, phone: str | None) -> str:
    """
    Hash contact identifiers to avoid storing raw PII.
    """
    base = f"{(email or '').strip().lower()}|{(phone or '').strip()}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def save_candidate_record(record: Dict[str, Any]) -> str:
    """
    Saves a JSON record to data/ as simulated backend storage.
    """
    cid = record.get("candidate_id", "unknown")
    path = os.path.join(DATA_DIR, f"candidate_{cid[:12]}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    return path