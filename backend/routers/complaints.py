from fastapi import APIRouter, Depends,Body
from sqlalchemy.orm import Session

from database import get_db
from schemas import ComplaintCreate
from models import Complaint

from services.ai_classifier import classify
from services.router_service import route
from services.ai_generator import generate_letter
from services.pdf_service import create_pdf

import uuid

router = APIRouter()
@router.post("/")
def submit_complaint(
    payload: ComplaintCreate,
    db: Session = Depends(get_db)
):

    category = classify(
        payload.complaint_text
    )

    routing = route(category)

    complaint_id = str(
        uuid.uuid4()
    )[:8]

    letter = generate_letter(
        category,
        payload.location,
        payload.complaint_text
    )

    pdf_path = create_pdf(
        complaint_id,
        letter
    )

    complaint = Complaint(

        complaint_id=complaint_id,

        citizen_name=payload.citizen_name,

        email=payload.email,

        phone=payload.phone,

        complaint_text=payload.complaint_text,

        issue_category=category,

        department=routing["department"],

        department_email=routing["email"],

        priority=routing["priority"],

        location=payload.location,

        latitude=payload.latitude,

        longitude=payload.longitude,

        generated_letter=letter,

        status="Submitted",

        email_sent=False,

        pdf_path=pdf_path
    )

    db.add(complaint)

    db.commit()

    db.refresh(complaint)

    return {
        "complaint_id": complaint_id,
        "category": category,
        "department": routing["department"],
        "priority": routing["priority"],
        "generated_letter": letter
    }


@router.get("/")
def get_complaints(
    db: Session = Depends(get_db)
):

    complaints = db.query(
        Complaint
    ).all()

    result = []

    for c in complaints:

        result.append({

            "id": c.id,

            "complaint_id": c.complaint_id,

            "citizen_name": c.citizen_name,

            "email": c.email,

            "phone": c.phone,

            "issue_category": c.issue_category,

            "complaint_text": c.complaint_text,

            "department": c.department,

            "department_email": c.department_email,

            "priority": c.priority,

            "location": c.location,

            "status": c.status,

            "generated_letter": c.generated_letter,

            "email_sent": c.email_sent,

            "pdf_path": c.pdf_path,

            "created_at": str(
                c.created_at
            ) if c.created_at else "",

            "updated_at": str(
                c.updated_at
            ) if c.updated_at else ""

        })

    return result


@router.get("/{complaint_id}")
def get_complaint_by_id(
    complaint_id: str,
    db: Session = Depends(get_db)
):

    complaint = db.query(
        Complaint
    ).filter(
        Complaint.complaint_id == complaint_id
    ).first()

    if not complaint:

        return {
            "message": "Complaint not found"
        }

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

        "created_at": str(
            complaint.created_at
        ) if complaint.created_at else "",

        "updated_at": str(
            complaint.updated_at
        ) if complaint.updated_at else ""
    }
@router.put("/{complaint_id}/status")
def update_complaint_status(
    complaint_id: str,
    payload: dict = Body(...),
    db: Session = Depends(get_db)):

    complaint = db.query(
        Complaint
    ).filter(
        Complaint.complaint_id == complaint_id
    ).first()

    if not complaint:
        return {
            "message": "Complaint not found"
        }

    complaint.status = payload.get(
        "status",
        complaint.status
    )

    db.commit()

    db.refresh(complaint)

    return {
        "message": "Status updated successfully",
        "complaint_id": complaint.complaint_id,
        "new_status": complaint.status
    }