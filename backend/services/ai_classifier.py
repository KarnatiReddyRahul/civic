def classify(text: str):

    text = text.lower()

    if "pothole" in text:
        return "Pothole"

    if "streetlight" in text:
        return "Streetlight"

    if "garbage" in text:
        return "Garbage"

    if "water" in text:
        return "Water Leakage"

    return "Other"