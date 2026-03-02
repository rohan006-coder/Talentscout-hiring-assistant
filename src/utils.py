import re
from typing import Dict, List

EXIT_KEYWORDS = {"exit", "quit", "bye", "goodbye", "stop", "end"}

def detect_exit(text: str) -> bool:
    t = (text or "").strip().lower()
    return any(k in t.split() for k in EXIT_KEYWORDS) or t in EXIT_KEYWORDS

def extract_contact_fields_light(text: str) -> Dict[str, str]:
    """
    Lightweight extraction using regex to avoid over-collecting sensitive data.
    We extract:
    - email
    - phone (very loose)
    - years of experience (number)
    - tech stack (if looks like comma-separated tech list)
    - name (if user says "my name is ...")
    - location (if user says "I am in ...")
    - desired positions (if user says "applying for ...")
    """
    out = {}

    email = re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", text)
    if email:
        out["email"] = email.group(1)

    phone = re.search(r"(\+?\d[\d\s\-\(\)]{8,}\d)", text)
    if phone:
        out["phone"] = phone.group(1).strip()

    yrs = re.search(r"(\d+(\.\d+)?)\s*(\+?\s*)?(years|yrs)", text, flags=re.I)
    if yrs:
        out["years_experience"] = yrs.group(1)

    name = re.search(r"(my name is|i am)\s+([A-Za-z][A-Za-z\s\.\-']{1,60})", text, flags=re.I)
    if name:
        out["full_name"] = name.group(2).strip()

    loc = re.search(r"(i am in|located in|based in)\s+(.+)", text, flags=re.I)
    if loc:
        out["location"] = loc.group(2).strip()

    pos = re.search(r"(applying for|looking for|interested in)\s+(.+)", text, flags=re.I)
    if pos:
        out["desired_positions"] = pos.group(2).strip()

    # Heuristic: tech stack (comma-separated list with common tech tokens)
    if "," in text and any(tok.lower() in text.lower() for tok in ["python", "java", "sql", "aws", "azure", "spark", "react", "django", "node", "snowflake"]):
        out.setdefault("tech_stack_raw", text.strip())

    return out

def normalize_tech_stack(raw: str) -> List[str]:
    if not raw:
        return []
    # split by comma, slash, pipe
    parts = re.split(r"[,/|]+", raw)
    techs = []
    for p in parts:
        t = p.strip()
        if not t:
            continue
        # remove trailing punctuation
        t = re.sub(r"[^\w\+\#\.\- ]+", "", t).strip()
        if t and t.lower() not in {x.lower() for x in techs}:
            techs.append(t)
    return techs[:25]

def pretty_stack(stack: List[str]) -> str:
    return ", ".join(stack) if stack else "(none detected)"