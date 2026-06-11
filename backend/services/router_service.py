import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "departments.json"

with open(
    DATA_PATH,
    "r",
    encoding="utf-8"
) as f:

    DEPTS = json.load(f)


def route(category, priority_override=None):

    info = DEPTS.get(
        category,
        {
            "department": "Municipal Corporation",
            "email": "municipal@demo.gov",
            "priority": "Medium"
        }
    )
    if priority_override:
        info = {**info, "priority": priority_override}
    return info