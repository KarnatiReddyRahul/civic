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

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model":"llama3",
                "prompt":prompt,
                "stream":False
            }
        )

        return response.json()["response"]

    except:

        return f"""
Complaint regarding {category}
at {location}

Description:
{description}
"""