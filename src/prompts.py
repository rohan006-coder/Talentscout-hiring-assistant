from typing import Dict, List

SYSTEM_PURPOSE = (
    "You are TalentScout Hiring Assistant for initial candidate screening in tech hiring. "
    "Your ONLY goals: (1) collect required candidate details, (2) ask technical questions based on declared tech stack, "
    "(3) stay coherent and context-aware, (4) do not request unnecessary sensitive data, "
    "(5) be concise and professional."
)

def build_info_gathering_prompt(system: str, candidate: dict, user_msg: str, next_question: str):
    """
    Used when LLM is enabled to keep the conversation coherent while collecting info.
    """
    return [
        {"role": "system", "content": system},
        {"role": "system", "content": f"Already collected candidate fields: {safe_candidate_snapshot(candidate)}"},
        {"role": "user", "content": user_msg},
        {"role": "system", "content": (
            "Task: If user answered the pending field, acknowledge and ask the next missing field. "
            "If user did not answer, politely re-ask the pending field. "
            "Do NOT deviate from screening purpose."
        )},
        {"role": "system", "content": f"Pending field question to ask now: {next_question}"},
    ]

def build_question_gen_prompt(system: str, candidate: dict):
    """
    Generates 3–5 technical questions per tech in the candidate stack.
    Output must be strict JSON.
    """
    stack = candidate.get("tech_stack", [])
    return [
        {"role": "system", "content": system},
        {"role": "system", "content": (
            "Generate technical screening questions. "
            "Rules: (1) For EACH technology listed, generate 3 to 5 questions. "
            "(2) Questions should be practical and appropriately challenging. "
            "(3) Avoid trick questions. "
            "(4) Output MUST be valid JSON object only (no markdown). "
            "JSON format: {\"Tech1\": [\"Q1\", \"Q2\", ...], \"Tech2\": [...]}."
        )},
        {"role": "system", "content": f"Candidate tech stack: {stack}"},
        {"role": "user", "content": "Generate questions now."},
    ]

def build_fallback_prompt(candidate: dict, user_msg: str) -> str:
    """
    Non-LLM fallback text.
    """
    return (
        "I may have missed that. Please answer the current question briefly. "
        "If you want to stop, type 'exit' or 'bye'."
    )

def build_end_prompt(candidate: dict) -> str:
    return (
        "✅ Thanks for your time! We’ve recorded your screening responses.\n\n"
        "**Next steps:** A TalentScout recruiter will review your details and reach out if there’s a match.\n\n"
        "You can close this chat now. Have a great day!"
    )

def safe_candidate_snapshot(candidate: dict) -> dict:
    """
    Removes raw contact info from prompt context when possible.
    """
    snap = dict(candidate)
    # Keep only presence flags for PII in prompts
    for k in ["email", "phone"]:
        if snap.get(k):
            snap[k] = "<provided>"
    return snap