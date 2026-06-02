from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Complaint

router = APIRouter()

@router.get("/stats")
def stats(db: Session = Depends(get_db)):

    total = db.query(Complaint).count()

    resolved = db.query(Complaint).filter(
        Complaint.status == "Resolved"
    ).count()

    pending = db.query(Complaint).filter(
        Complaint.status != "Resolved"
    ).count()

    high_priority = db.query(Complaint).filter(
        Complaint.priority == "High"
    ).count()

    return {
        "total_complaints": total,
        "resolved": resolved,
        "pending": pending,
        "high_priority": high_priority
    }