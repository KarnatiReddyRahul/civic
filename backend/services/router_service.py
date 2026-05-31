import json

with open(
    "data/departments.json",
    "r",
    encoding="utf-8"
) as f:

    DEPTS = json.load(f)


def route(category):

    return DEPTS.get(
        category,
        {
            "department": "Municipal Corporation",
            "email": "municipal@demo.gov",
            "priority": "Medium"
        }
    )