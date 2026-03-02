# 🤖 TalentScout — Hiring Assistant

An intelligent, interactive screening chatbot designed to streamline initial candidate screening in tech hiring. TalentScout collects candidate details, assesses their tech stack, and generates personalized technical questions dynamically.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Installation Instructions](#installation-instructions)
- [Usage Guide](#usage-guide)
- [Technical Details](#technical-details)
- [Prompt Design](#prompt-design)
- [Challenges & Solutions](#challenges--solutions)
- [Project Structure](#project-structure)
- [Code Quality](#code-quality)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## 📖 Project Overview

**TalentScout** is a Streamlit-based hiring assistant that automates the initial candidate screening process. Instead of manually asking standardized questions, the bot:

1. **Collects candidate information** — Full name, email, phone, years of experience, desired positions, location
2. **Analyzes tech stack** — Extracts and normalizes the candidate's declared technologies
3. **Generates tailored questions** — Creates 3–5 technical questions per technology (using either LLM or rule-based approach)
4. **Stores anonymized records** — Saves screening data with hashed identifiers for privacy
5. **Provides sentiment analysis** (optional) — Real-time sentiment feedback during conversation

The bot intelligently handles unknown technologies by generating dynamic questions based on the tech name, ensuring every candidate receives relevant screening regardless of their stack.

---

## ✨ Features

- 🧠 **Smart Information Extraction** — Contextual field parsing that accepts natural language responses
- 📊 **Dual Question Generation**:
  - **LLM-powered** (OpenAI GPT) for sophisticated, creative questions
  - **Rule-based fallback** for reliable offline operation with predefined questions
- 🎯 **Dynamic Tech Detection** — Generates questions for any technology, even those not in the default database
- 💾 **Privacy-First Data Storage** — Hashed candidate IDs, anonymized records
- 🎨 **Beautiful UI** — Modern Streamlit interface with styled chat bubbles and gradient headers
- 🛑 **Exit Handling** — Graceful session termination with keywords (exit, quit, bye)
- 📈 **Sentiment Analysis** (optional) — Real-time emotion tracking during screening

---

## 🚀 Installation Instructions

### Prerequisites

- Python 3.9 or higher
- Git
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone https://github.com/rohan006-coder/Talentscout-hiring-assistant.git
cd Talentscout-hiring-assistant
```

### Step 2: Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `streamlit==1.37.1` — Web framework for rapid UI development
- `openai>=1.40.0` — OpenAI API client (optional for LLM features)
- `vaderSentiment==3.3.2` — Sentiment analysis library (optional)

### Step 4: (Optional) Set OpenAI API Key

To enable LLM-powered question generation:

```bash
# Windows (PowerShell)
$env:OPENAI_API_KEY = "your-api-key-here"

# macOS/Linux
export OPENAI_API_KEY="your-api-key-here"
```

### Step 5: Run the Application

```bash
streamlit run app.py
```

The app will launch at `http://localhost:8501`

---

## 📖 Usage Guide

### Starting a Screening Session

1. **Open the app** at `http://localhost:8501`
2. **Read the greeting** — The bot introduces itself and explains the process
3. **Answer questions in order**:
   - Full name
   - Email address
   - Phone number
   - Years of experience
   - Desired positions
   - Current location
   - Tech stack (comma-separated, e.g., "Python, Django, PostgreSQL")

### Flexible Input Handling

The bot accepts **natural language** for most fields:
- ✅ "My name is John Doe" → Extracts "John Doe"
- ✅ "John Doe" → Directly accepts as name
- ✅ "5 years" → Extracts experience
- ✅ "john@example.com" → Detects email
- ✅ "Python, Django, AWS" → Detects tech stack

### Technical Questions Phase

After collecting all information:
- The bot displays your detected tech stack
- For each technology, you'll answer 3–5 technical questions
- Questions are **specific to your stack** (e.g., if you list Java, Java-specific questions appear)
- Answer briefly; it's acceptable to say "not sure"

### Settings (Sidebar)

- **Use LLM (OpenAI)** — Toggle to enable/disable AI-powered question generation
- **Save anonymized session** — Persist screening data locally
- **Show sentiment signal** — Display real-time sentiment feedback
- **Exit keywords** — Review how to exit (exit, quit, bye)

### Exit Session

Type any of these to end the screening:
- `exit`
- `quit`
- `bye`
- `goodbye`
- `stop`
- `end`

---

## 🛠️ Technical Details

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit 1.37.1 | Interactive web UI |
| **NLP/LLM** | OpenAI GPT (optional) | Dynamic question generation |
| **Sentiment** | VADER (optional) | Emotion analysis |
| **Storage** | JSON + File system | Candidate records |
| **VCS** | Git | Version control |

### Architecture

```
app.py (Main entry point)
├── Session Management
│   └── Candidate state tracking (name, email, tech stack, etc.)
├── Chat Logic
│   ├── Greeting stage
│   ├── Information collecting stage
│   ├── Technical questions stage
│   └── Closing stage
└── UI Rendering
    ├── Custom CSS styling
    ├── Chat bubbles
    └── Sidebar controls

src/
├── llm.py
│   └── LLM client for OpenAI API interaction
├── prompts.py
│   └── Prompt templates for info gathering and question generation
├── question_bank.py
│   ├── Default questions for known technologies
│   └── Dynamic fallback for unknown technologies
├── utils.py
│   ├── Field extraction (regex-based)
│   ├── Tech stack normalization
│   └── Exit detection
└── storage.py
    └── Candidate record saving (anonymized)

data/
└── Stores JSON files with candidate screening results
```

### Key Modules

#### `app.py` (Main Application)
- Streamlit session state management
- Multi-stage conversation flow
- Custom CSS injection for styling
- Context-aware field extraction

#### `src/llm.py` (LLM Integration)
```python
class LLMClient:
    - is_ready(): Check if OpenAI API key is available
    - chat(): Send messages to GPT and retrieve responses
    - generate_questions(): Generate JSON-formatted question sets
```

#### `src/question_bank.py` (Question Management)
```python
DEFAULT_QUESTIONS: Dict[str, List[str]]
    - Predefined questions for: Python, SQL, Django, AWS, Azure, Spark, Java, JavaScript
    
rule_based_questions(tech_stack):
    - Matches each tech against defaults
    - Falls back to dynamic templates for unknown techs
    - Ensures 3–5 questions per technology
```

#### `src/utils.py` (Text Processing)
```python
extract_contact_fields_light(): Pattern-based extraction
extract_field_contextually(): Context-aware fallback extraction
normalize_tech_stack(): Tech stack parsing and deduplication
```

#### `src/storage.py` (Data Persistence)
```python
hash_contact(): SHA256 hash for PII anonymization
save_candidate_record(): Write JSON to data/ directory
```

---

## 🧠 Prompt Design

### Information Gathering Prompts

When LLM is enabled, the bot uses:

```python
build_info_gathering_prompt(system, candidate, user_msg, next_question)
```

**Purpose:** Keep the conversation coherent while collecting required fields.

**Example Flow:**
1. System tells LLM: "You are TalentScout Hiring Assistant"
2. System provides: "Already collected: [name, email, ...]"
3. System sets: "Pending field: years_experience"
4. Bot acknowledges previous answer and asks next question

### Question Generation Prompts

For dynamic question creation:

```python
build_question_gen_prompt(system, candidate)
```

**Constraints:**
- Generates **3–5 questions per technology**
- Practical, appropriately challenging questions
- No trick questions
- Output must be **strict JSON**

**Example Output:**
```json
{
  "Python": [
    "Explain the difference between a list and a tuple. When would you use each?",
    "What is a generator in Python, and why is it useful?",
    "How does Python manage memory (reference counting / garbage collection)?"
  ],
  "Django": [
    "Explain Django's MVT pattern and how a request is processed.",
    "How do you optimize Django ORM queries with select_related/prefetch_related?"
  ]
}
```

### Fallback Prompts

For unknown technologies, the bot generates dynamic questions:

```python
"What are core concepts you rely on when working with {tech}?"
"Describe a project where you used {tech}. What was your role and impact?"
"What are common pitfalls or performance issues in {tech}, and how do you address them?"
"How do you approach learning new features or updates in {tech}?"
"What tools or libraries commonly complement your work with {tech}?"
```

---

## 🔧 Challenges & Solutions

### Challenge 1: Handling Flexible User Input

**Problem:** Users don't always enter data in expected formats. E.g., "my name is John" vs. just "John".

**Solution:** 
- Implemented **two-tier extraction**:
  1. Pattern-based extraction (regex for emails, phone numbers)
  2. Context-aware fallback that's lenient for the currently-missing field
- For name field: Accept any reasonable text when asking for a name
- For email: Validate email pattern, but accept if provided naturally

**Code:**
```python
def extract_field_contextually(user_input: str, field: str):
    if field == "full_name":
        # Accept any non-empty text as a name
        if len(clean) > 1:
            return clean
    # ... similar for other fields
```

### Challenge 2: Generating Questions for Unknown Technologies

**Problem:** Can't hard-code questions for every possible tech (Rust, Elixir, Go, etc.).

**Solution:**
- Created a **fallback template system** that dynamically inserts the tech name
- Generates 5 generic but relevant questions for any technology
- If tech *is* in the database, use curated questions; otherwise use templates

**Code:**
```python
if key in DEFAULT_QUESTIONS:
    out[tech] = DEFAULT_QUESTIONS[key][:5]
else:
    out[tech] = [
        f"What are core concepts you rely on when working with {tech}?",
        f"Describe a project where you used {tech}. What was your role and impact?",
        # ... more dynamic questions
    ]
```

### Challenge 3: Privacy & PII Handling

**Problem:** Storing raw candidate emails and phone numbers violates privacy.

**Solution:**
- Hash contact information using SHA256
- Store only hashed identifier (`candidate_id`) and non-sensitive fields
- Anonymized records: name, experience, positions, location, tech stack
- PII (email, phone) excluded from persistent storage

**Code:**
```python
def hash_contact(email: str | None, phone: str | None) -> str:
    base = f"{(email or '').strip().lower()}|{(phone or '').strip()}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()
```

### Challenge 4: Chat Bubble Visibility

**Problem:** Initial CSS styling made bot text too light to read.

**Solution:**
- Darkened text color to `#111` (near black)
- Applied to both assistant and user bubbles
- Ensured sufficient contrast against backgrounds

**CSS:**
```css
.assistant-bubble { color: #111; }
.user-bubble { color: #111; }
```

### Challenge 5: UI Attractiveness

**Problem:** Default Streamlit interface looked plain.

**Solution:**
- Added custom CSS with:
  - Gradient header (blue to light blue)
  - Styled chat bubbles with emojis (🤖 for bot, 🙂 for user)
  - Centered, constrained layout
  - Modern color palette (#f0f4f8 background, #4a6fa5 primary)
  - Border-radius and shadows for depth

---

## 📁 Project Structure

```
talentscout-hiring-assistant/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
├── data/
│   ├── .gitkeep                   # Placeholder for data directory
│   └── candidate_*.json           # Saved screening records
├── src/
│   ├── __init__.py               # Package init (implicit)
│   ├── llm.py                    # OpenAI LLM client
│   ├── prompts.py                # Prompt templates
│   ├── question_bank.py          # Question generation logic
│   ├── storage.py                # Data persistence
│   └── utils.py                  # Utility functions
└── .venv/                        # Virtual environment (not in repo)
```

---

## 📊 Code Quality

### Structure & Readability

✅ **Modular Design**
- Separated concerns: UI (app.py), LLM (llm.py), Q&A (question_bank.py), Storage (storage.py)
- Each module has a single responsibility
- Easy to test and extend

✅ **Naming Conventions**
- Clear, descriptive function and variable names
- Comments explain complex logic
- Type hints where applicable (`str | None`, `Dict[str, List[str]]`)

✅ **Best Practices**
- No hardcoded credentials (uses environment variables)
- Graceful error handling for missing dependencies
- Session state management to prevent data loss

### Documentation

✅ **Docstrings**
```python
def rule_based_questions(tech_stack: List[str]) -> Dict[str, List[str]]:
    """
    Creates 3–5 questions per detected technology.
    If unknown tech: produce generic questions.
    """
```

✅ **Inline Comments**
```python
# Two-tier extraction: first try patterns, then context-aware fallback
extracted = extract_contact_fields_light(user_input)
if missing and not extracted:
    current_field = missing[0]
    val = extract_field_contextually(user_input, current_field)
```

### Version Control

✅ **Git Workflow**
- Clear commit history: "initial commit" with all core files
- Remote tracking: `origin/main` synced with GitHub
- No merge conflicts; linear history

✅ **Repository**
```
https://github.com/rohan006-coder/Talentscout-hiring-assistant
```

---

## 🚀 Future Enhancements

### Short-term
- [ ] Add a database (PostgreSQL/MongoDB) for scalable storage
- [ ] Implement role-based access (recruiter dashboard, admin panel)
- [ ] Enhanced sentiment tracking with emotion classification
- [ ] Email notification to recruiters after screening completion

### Medium-term
- [ ] Multi-language support (Spanish, Hindi, etc.)
- [ ] Video screening capability
- [ ] Scoring rubric for objective evaluation
- [ ] Integration with ATS (Applicant Tracking System)

### Long-term
- [ ] Skill-matching algorithm to suggest job recommendations
- [ ] Continued learning from past screening outcomes
- [ ] Voice-based interviews with speech-to-text
- [ ] ML-based candidate ranking

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit with clear messages (`git commit -m "Add feature X"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the **MIT License** — see the LICENSE file for details.

---

## 📞 Support & Contact

For questions or feedback:
- **GitHub Issues:** [Open an issue](https://github.com/rohan006-coder/Talentscout-hiring-assistant/issues)
- **Email:** yeluguri1234.rohan@gmail.com

---

## 🎯 Quick Start

```bash
# Clone
git clone https://github.com/rohan006-coder/Talentscout-hiring-assistant.git
cd Talentscout-hiring-assistant

# Setup
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt

# Run
streamlit run app.py

# Open browser to http://localhost:8501
```

---

**Built with ❤️ using Streamlit, Python, and a passion for great hiring experiences.**

Happy screening! 🎉
