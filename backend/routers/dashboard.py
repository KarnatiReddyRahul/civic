from fastapi import APIRouter
from sqlalchemy import func

router = APIRouter()

@router.get("/stats")
def stats():

    return {
        "total_complaints": 120,
        "resolved": 70,
        "pending": 50,
        "high_priority": 20
    }