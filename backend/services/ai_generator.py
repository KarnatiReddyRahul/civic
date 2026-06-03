import os

import requests


def generate_letter(
    category,
    location,
    description
):

    prompt = f"""
Generate a professional civic complaint.

Issue:
{category}

Location:
{location}

Description:
{description}
"""

    model_host = os.environ.get(
        "AI_GENERATOR_BASE",
        "http://localhost:11434"
    )

    try:

        response = requests.post(
            f"{model_host}/api/generate",
            json={
                "model":"llama3",
                "prompt":prompt,
                "stream":False
            },
            timeout=10
        )

        response.raise_for_status()
        return response.json().get("response", "")

    except Exception:

        return f"""
Complaint regarding {category}
at {location}

Description:
{description}
"""