from backend.database import SessionLocal
from backend.models import Complaint
from backend.services.ai_classifier import classify
from backend.services.router_service import route
from backend.services.ai_generator import generate_letter
from backend.services.pdf_service import create_pdf

import uuid


def get_all_complaints():
    db = SessionLocal()

    try:
        return db.query(Complaint).order_by(Complaint.created_at.desc()).all()

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


def create_complaint(payload):
    db = SessionLocal()

    try:
        category = classify(payload["complaint_text"])
        routing = route(category)
        complaint_id = str(uuid.uuid4())[:8]

        letter = generate_letter(
            category,
            payload.get("location", ""),
            payload["complaint_text"]
        )

        pdf_path = create_pdf(
            complaint_id,
            letter
        )

        complaint = Complaint(
            complaint_id=complaint_id,
            citizen_name=payload.get("citizen_name", "Anonymous"),
            email=payload.get("email", "user@example.com"),
            phone=payload.get("phone", "0000000000"),
            complaint_text=payload["complaint_text"],
            issue_category=category,
            department=routing["department"],
            department_email=routing["email"],
            priority=routing["priority"],
            location=payload.get("location", ""),
            latitude=payload.get("latitude"),
            longitude=payload.get("longitude"),
            generated_letter=letter,
            status="Submitted",
            email_sent=False,
            pdf_path=pdf_path
        )

        db.add(complaint)
        db.commit()
        db.refresh(complaint)

        return complaint

    finally:
        db.close()


def complaint_to_dict(complaint):
    return {
        "id": complaint.id,
        "complaint_id": complaint.complaint_id,
        "citizen_name": complaint.citizen_name,
        "email": complaint.email,
        "phone": complaint.phone,
        "issue_category": complaint.issue_category,
        "complaint_text": complaint.complaint_text,
        "department": complaint.department,
        "department_email": complaint.department_email,
        "priority": complaint.priority,
        "location": complaint.location,
        "status": complaint.status,
        "generated_letter": complaint.generated_letter,
        "email_sent": complaint.email_sent,
        "pdf_path": complaint.pdf_path,
        "created_at": str(complaint.created_at) if complaint.created_at else "",
        "updated_at": str(complaint.updated_at) if complaint.updated_at else ""
    }


def get_all_complaints_dict():
    return [
        complaint_to_dict(c)
        for c in get_all_complaints()
    ]