import os
import time
import re
import streamlit as st

from src.utils import (
    EXIT_KEYWORDS,
    detect_exit,
    extract_contact_fields_light,
    normalize_tech_stack,
    pretty_stack,
)
from src.llm import LLMClient
from src.prompts import (
    SYSTEM_PURPOSE,
    build_info_gathering_prompt,
    build_question_gen_prompt,
    build_fallback_prompt,
    build_end_prompt,
)
from src.question_bank import rule_based_questions
from src.storage import save_candidate_record, hash_contact

st.set_page_config(page_title="TalentScout Hiring Assistant", page_icon="🤖", layout="centered")

# inject some custom CSS to make the layout and bubbles more attractive
st.markdown(
    """
    <style>
    body {background-color: #f0f4f8; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;}
    h1 {color: #4a6fa5; font-weight: bold;}
    .chat-container {max-width: 700px; margin: auto; padding: 10px;}
    .assistant-bubble {background:#ffffff; border:1px solid #ddd; padding:12px; border-radius:10px; margin:8px 0; position:relative; color:#111;}
    .assistant-bubble:before {content: '🤖'; position:absolute; left:-28px; top:0; font-size:20px;}
    .user-bubble {background:#dcf8c6; border:1px solid #ccc; padding:12px; border-radius:10px; margin:8px 0; text-align:right; position:relative; color:#111;}
    .user-bubble:after {content:'🙂'; position:absolute; right:-28px; top:0; font-size:20px;}
    .sidebar .stButton>button {background-color:#4a6fa5; color:white;}
    .st-chat-input {border-radius:8px;}
    .footer-note {text-align:center; font-size:0.85em; color:#666;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h1 style='text-align:center; background: linear-gradient(90deg, #4a6fa5, #8ab4f8); -webkit-background-clip: text; color: transparent;'>🤖 TalentScout — Hiring Assistant</h1>", unsafe_allow_html=True)
st.caption(
    "<div style='text-align:center; font-size:1.1em;'>Initial screening chatbot: collects basic details and generates technical questions based on your declared tech stack.</div>",
    unsafe_allow_html=True,
)

st.markdown("<hr style='margin:20px 0;'/>", unsafe_allow_html=True)

with st.expander("Privacy note"):
    st.write(
        "This demo stores only **simulated/anonymized** screening data locally (hashed identifiers), "
        "not raw PII. You can disable saving in the sidebar."
    )

# Sidebar settings
st.sidebar.markdown("<h2 style='color:#4a6fa5;'>🎯 Settings</h2>", unsafe_allow_html=True)
use_llm = st.sidebar.toggle("Use LLM (OpenAI)", value=False)
save_data = st.sidebar.toggle("Save anonymized session", value=True)
sentiment_on = st.sidebar.toggle("Show sentiment signal (optional)", value=False)
st.sidebar.markdown("---")
st.sidebar.write("Exit keywords: " + ", ".join(sorted(EXIT_KEYWORDS)))

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "candidate" not in st.session_state:
    st.session_state.candidate = {
        "full_name": None,
        "email": None,
        "phone": None,
        "years_experience": None,
        "desired_positions": None,
        "location": None,
        "tech_stack_raw": None,
        "tech_stack": [],
        "stage": "greeting",  # greeting -> collecting -> questions -> closing
        "questions": {},
        "answers": {},
        "created_at": time.time(),
    }

# LLM client (only used if toggle on and API key exists)
llm = LLMClient()

def assistant_say(text: str):
    st.session_state.messages.append({"role": "assistant", "content": text})

def user_say(text: str):
    st.session_state.messages.append({"role": "user", "content": text})

def render_chat():
    # wrap in container
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for m in st.session_state.messages:
        role = m.get("role")
        content = m.get("content", "")
        if role == "assistant":
            st.markdown(f"<div class='assistant-bubble'>{content}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='user-bubble'>{content}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def get_missing_fields(cand: dict):
    required = ["full_name", "email", "phone", "years_experience", "desired_positions", "location", "tech_stack_raw"]
    return [k for k in required if not cand.get(k)]

def next_question_for_missing(cand: dict):
    missing = get_missing_fields(cand)
    if not missing:
        return None

    order = {
        "full_name": "What is your full name?",
        "email": "What is your email address?",
        "phone": "What is your phone number?",
        "years_experience": "How many years of experience do you have? (e.g., 3, 5.5)",
        "desired_positions": "What position(s) are you applying for? (e.g., Data Engineer, ML Engineer)",
        "location": "What is your current location (city, country / state)?",
        "tech_stack_raw": "Please list your tech stack (languages, frameworks, databases, tools). Example: Python, Django, Postgres, AWS",
    }
    return order[missing[0]]

def extract_field_contextually(user_input: str, field: str):
    """
    Context-aware extraction for a specific field.
    If user is answering for a particular field, be more lenient.
    """
    clean = user_input.strip()
    if not clean:
        return None
    
    if field == "full_name":
        # Accept any non-empty text that looks like a name (at least 2 chars, no obvious gibberish)
        if len(clean) > 1 and not clean.startswith("http"):
            return clean
    elif field == "email":
        # Look for email pattern
        match = re.search(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", user_input)
        if match:
            return match.group(1)
    elif field == "phone":
        # Look for phone pattern
        match = re.search(r"(\+?\d[\d\s\-\(\)]{8,}\d)", user_input)
        if match:
            return match.group(1).strip()
    elif field == "years_experience":
        # Look for number followed by 'years' or by itself
        match = re.search(r"(\d+(\.\d+)?)", user_input)
        if match:
            return match.group(1)
    elif field == "location":
        # Accept any meaningful text (avoid single chars)
        if len(clean) > 2:
            return clean
    elif field == "desired_positions":
        # Accept any meaningful text
        if len(clean) > 2:
            return clean
    elif field == "tech_stack_raw":
        # Accept as is if it looks like tech (contains comma or known tech words)
        if "," in clean or any(tok.lower() in clean.lower() for tok in ["python", "java", "sql", "aws", "azure", "spark", "react", "django", "node", "snowflake", "javascript", "typescript", "golang", "rust"]):
            return clean
    
    return None

def maybe_show_sentiment(latest_user_text: str):
    if not sentiment_on:
        return
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
        score = analyzer.polarity_scores(latest_user_text)
        st.sidebar.info(f"Sentiment (compound): {score['compound']:.2f}")
    except Exception:
        st.sidebar.warning("Sentiment library not installed. Install `vaderSentiment` or turn this off.")

# Greeting
if st.session_state.candidate["stage"] == "greeting" and not st.session_state.messages:
    assistant_say(
        "Hi! I’m **TalentScout Hiring Assistant** 🤝\n\n"
        "I’ll collect a few details for initial screening and then ask a few **technical questions** "
        "based on your **tech stack**. You can type **'exit'**, **'quit'**, **'bye'** anytime to stop."
    )
    st.session_state.candidate["stage"] = "collecting"
    assistant_say(next_question_for_missing(st.session_state.candidate))

render_chat()

# Chat input
user_input = st.chat_input("Type your response…")
if user_input:
    # Exit handling
    if detect_exit(user_input):
        user_say(user_input)
        end_msg = build_end_prompt(st.session_state.candidate)
        assistant_say(end_msg)
        st.session_state.candidate["stage"] = "closing"
        render_chat()
        st.stop()

    user_say(user_input)
    maybe_show_sentiment(user_input)

    cand = st.session_state.candidate

    # Collecting stage: parse fields in a lightweight way from user message
    if cand["stage"] == "collecting":
        # First try standard extraction (for patterns like "my name is X", "email@com", etc.)
        extracted = extract_contact_fields_light(user_input)
        
        # If nothing extracted, try context-aware extraction for the missing field
        missing = get_missing_fields(cand)
        if missing and not extracted:
            current_field = missing[0]
            val = extract_field_contextually(user_input, current_field)
            if val:
                extracted[current_field] = val
        
        for k, v in extracted.items():
            if v and not cand.get(k):
                cand[k] = v

        # If tech stack just provided, normalize it
        if cand.get("tech_stack_raw") and not cand.get("tech_stack"):
            cand["tech_stack"] = normalize_tech_stack(cand["tech_stack_raw"])

        # If missing fields remain, ask next
        nxt = next_question_for_missing(cand)
        if nxt:
            # Fallback: if user says unrelated stuff, politely re-ask the pending field
            if use_llm and llm.is_ready():
                prompt = build_info_gathering_prompt(SYSTEM_PURPOSE, cand, user_input, nxt)
                reply = llm.chat(prompt)
                assistant_say(reply)
            else:
                assistant_say(nxt)
        else:
            # Move to question stage
            cand["stage"] = "questions"
            assistant_say(
                f"Thanks, **{cand['full_name']}**. I captured your stack as:\n\n"
                f"**{pretty_stack(cand['tech_stack'])}**\n\n"
                "Now I’ll ask a few technical questions (3–5 per technology). "
                "Answer briefly; it’s okay to say 'not sure'."
            )

            # Generate questions (LLM if available, else rule-based)
            stack = cand["tech_stack"]
            if use_llm and llm.is_ready():
                q_prompt = build_question_gen_prompt(SYSTEM_PURPOSE, cand)
                questions = llm.generate_questions(q_prompt)
            else:
                questions = rule_based_questions(stack)

            cand["questions"] = questions
            # Ask first tech questions
            first_tech = list(questions.keys())[0] if questions else None
            if not first_tech:
                assistant_say("I couldn’t detect technologies in your stack. Please re-enter your tech stack.")
                cand["stage"] = "collecting"
                cand["tech_stack_raw"] = None
                cand["tech_stack"] = []
                assistant_say(next_question_for_missing(cand))
            else:
                cand["current_tech"] = first_tech
                cand["current_q_index"] = 0
                assistant_say(f"### {first_tech}\n\n1) {questions[first_tech][0]}")

    elif cand["stage"] == "questions":
        # Save the answer for current question
        tech = cand.get("current_tech")
        idx = cand.get("current_q_index", 0)

        if tech:
            cand["answers"].setdefault(tech, {})
            cand["answers"][tech][str(idx)] = user_input

        # Move to next question
        questions = cand.get("questions", {})
        techs = list(questions.keys())
        if not techs:
            assistant_say(build_fallback_prompt(cand, user_input))
        else:
            tech_i = techs.index(tech) if tech in techs else 0
            idx += 1
            if idx < len(questions[tech]):
                cand["current_q_index"] = idx
                assistant_say(f"{idx+1}) {questions[tech][idx]}")
            else:
                # Next tech
                tech_i += 1
                if tech_i < len(techs):
                    cand["current_tech"] = techs[tech_i]
                    cand["current_q_index"] = 0
                    t = techs[tech_i]
                    assistant_say(f"### {t}\n\n1) {questions[t][0]}")
                else:
                    # Done
                    cand["stage"] = "closing"
                    assistant_say(build_end_prompt(cand))

                    # Save anonymized record
                    if save_data:
                        record = {
                            "candidate_id": hash_contact(cand.get("email"), cand.get("phone")),
                            "full_name": cand.get("full_name"),
                            "years_experience": cand.get("years_experience"),
                            "desired_positions": cand.get("desired_positions"),
                            "location": cand.get("location"),
                            "tech_stack": cand.get("tech_stack"),
                            "questions": cand.get("questions"),
                            "answers": cand.get("answers"),
                            "created_at": cand.get("created_at"),
                        }
                        save_candidate_record(record)

    else:
        assistant_say("This session is closed. Refresh the page to start a new screening.")

    render_chat()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align:center; font-size:0.9em; color:#666;'>" \
    "Demo for the TalentScout screening assistant &mdash; built with &#10084; and Streamlit" \
    "</div>",
    unsafe_allow_html=True,
)