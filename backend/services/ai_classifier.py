import os

import requests

CATEGORIES = [
    "Pothole", "Streetlight", "Garbage",
    "Water Leakage", "Drainage Issue"
]


def classify(text: str, location: str = "") -> tuple[str, str]:

    model_host = os.environ.get(
        "AI_GENERATOR_BASE",
        "http://localhost:11434"
    )

    prompt = (
        f"Classify the following civic complaint and determine its priority.\n"
        f"Category must be one of: {', '.join(CATEGORIES)}.\n"
        f"Priority must be one of: High, Medium, Low.\n"
        f"Consider urgency keywords (danger, accident, children, school, hospital, emergency -> High).\n"
        f"If location is mentioned, consider area sensitivity (school/hospital area -> High).\n"
        f"Respond with exactly: Category: <name> | Priority: <level>\n\n"
        f"Complaint: {text}\n"
        f"Location: {location}\n\n"
        f"Response:"
    )

    try:
        resp = requests.post(
            f"{model_host}/api/generate",
            json={"model": "llama3", "prompt": prompt, "stream": False},
            timeout=10,
        )
        resp.raise_for_status()
        result = resp.json().get("response", "").strip()

        category = None
        priority = None
        for line in result.split("\n"):
            line_lower = line.lower()
            if "category:" in line_lower:
                for cat in CATEGORIES:
                    if cat.lower() in line_lower:
                        category = cat
                        break
            if "priority:" in line_lower:
                for p in ("High", "Medium", "Low"):
                    if p.lower() in line_lower:
                        priority = p
                        break

        if category and priority:
            return category, priority
    except Exception:
        pass

    t = text.lower()
    tl = t + " " + location.lower()

    if "drain" in tl or "flood" in tl:
        category = "Drainage Issue"
    elif "water" in tl or "leak" in tl:
        category = "Water Leakage"
    elif "pothole" in tl or ("road" in tl and "damage" in tl):
        category = "Pothole"
    elif "garbage" in tl or "waste" in tl or "dump" in tl:
        category = "Garbage"
    elif "streetlight" in tl or "light" in tl:
        category = "Streetlight"
    else:
        category = "Other"

    urgency_words = [
        "danger", "accident", "emergency", "urgent", "critical",
        "school", "hospital", "clinic", "children", "elderly",
        "main road", "highway", "busy", "market", "injury",
        "block", "flood", "overflow", "stuck", "collapse"
    ]
    if any(w in tl for w in urgency_words):
        priority = "High"
    elif any(w in tl for w in ["slight", "minor", "small", "cosmetic"]):
        priority = "Low"
    else:
        priority = "Medium"

    return category, priority