from typing import Dict, List

DEFAULT_QUESTIONS: Dict[str, List[str]] = {
    "python": [
        "Explain the difference between a list and a tuple. When would you use each?",
        "What is a generator in Python, and why is it useful?",
        "How do you handle exceptions in Python? Give an example with try/except/finally.",
        "What are decorators and a common use case?",
        "How does Python manage memory (reference counting / garbage collection) at a high level?"
    ],
    "sql": [
        "What’s the difference between INNER JOIN and LEFT JOIN? Give a use case.",
        "How would you find duplicate records in a table?",
        "Explain window functions and one practical example (ROW_NUMBER, SUM OVER, etc.).",
        "What is an index and how does it affect query performance?",
        "How do you design a schema for analytics vs OLTP?"
    ],
    "django": [
        "Explain Django’s MVT pattern and how a request is processed.",
        "What are migrations and how do you handle schema changes safely?",
        "How do you optimize Django ORM queries (select_related/prefetch_related)?",
        "What is middleware in Django and a common use case?",
        "How would you secure a Django app (CSRF, auth, secrets)?"
    ],
    "aws": [
        "Explain the difference between S3, EBS, and EFS.",
        "How would you design a secure data pipeline on AWS?",
        "What is IAM and how do roles differ from users?",
        "How do you monitor and alert on failures in AWS services?",
        "Describe a serverless use case using Lambda."
    ],
    "azure": [
        "What’s the difference between Azure Blob Storage and ADLS Gen2?",
        "Explain how you would build an ELT pipeline using ADF + Databricks/Synapse.",
        "How do Managed Identities help with security?",
        "How would you implement monitoring and alerting (Log Analytics, App Insights)?",
        "What is the purpose of Event Hubs vs Service Bus?"
    ],
    "spark": [
        "What’s the difference between transformations and actions in Spark?",
        "Explain shuffle and how you reduce shuffle in Spark jobs.",
        "When would you use repartition vs coalesce?",
        "How do you handle skewed data in Spark?",
        "Explain caching/persist and when it helps."
    ],
    "java": [
        "What are the core object‑oriented principles in Java and how do you apply them?",
        "Explain the difference between `==` and `equals()` in Java.",
        "How does the Java garbage collector work at a high level?",
        "What is the Java memory model and why is it important?",
        "Describe how you would handle exceptions and provide a brief example."
    ],
    "javascript": [
        "Explain the difference between `var`, `let`, and `const` in JavaScript.",
        "What is event bubbling and how can you prevent it?",
        "Describe how promises work and give an example use case.",
        "What is the difference between `==` and `===`?",
        "How do you optimize performance in a JavaScript‑heavy web app?"
    ],
}

def rule_based_questions(tech_stack: List[str]) -> Dict[str, List[str]]:
    """
    Creates 3–5 questions per detected technology.
    If unknown tech: produce generic questions.
    """
    out: Dict[str, List[str]] = {}
    for tech in tech_stack:
        key = tech.strip().lower()
        if key in DEFAULT_QUESTIONS:
            out[tech] = DEFAULT_QUESTIONS[key][:5]
        else:
            # tech not in our hard‑coded list; still generate a few basic, customised questions
            out[tech] = [
                f"What are core concepts you rely on when working with {tech}?",
                f"Describe a project where you used {tech}. What was your role and impact?",
                f"What are common pitfalls or performance issues in {tech}, and how do you address them?",
                f"How do you approach learning new features or updates in {tech}?",
                f"What tools or libraries commonly complement your work with {tech}?",
            ]
    # Ensure 3–5 questions each
    for tech, qs in out.items():
        out[tech] = qs[:5] if len(qs) > 5 else qs
        while len(out[tech]) < 3:
            out[tech].append(f"How do you test or validate work done in {tech}?")
    return out