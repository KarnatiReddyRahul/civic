from backend.database import SessionLocal
from backend.models import Complaint


def get_all_complaints():
    db = SessionLocal()

    try:
        return db.query(Complaint).all()

    finally:
        db.close()


def get_complaint_by_id(cid):
    db = SessionLocal()

    try:
        return (
            db.query(Complaint)
            .filter(Complaint.complaint_id == cid)
            .first()
        )

    finally:
        db.close()


def update_complaint_status(
    complaint_id,
    new_status
):
    db = SessionLocal()

    try:

        complaint = (
            db.query(Complaint)
            .filter(
                Complaint.complaint_id == complaint_id
            )
            .first()
        )

        if complaint:

            complaint.status = new_status

            db.commit()

            db.refresh(complaint)

        return complaint

    finally:

        db.close()