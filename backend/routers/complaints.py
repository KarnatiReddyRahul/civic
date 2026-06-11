import uuid
from pathlib import Path

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Complaint
from backend.schemas import ComplaintCreate
from backend.services.ai_classifier import classify
from backend.services.ai_generator import generate_letter
from backend.services.email_service import send_email
from backend.services.pdf_service import create_pdf
from backend.services.router_service import route

router = APIRouter()

GENERATED_PDFS_DIR = Path(__file__).resolve().parent.parent / "generated_pdfs"


@router.post("/")
def submit_complaint(
    payload: ComplaintCreate,
    db: Session = Depends(get_db)
):

    category, priority = classify(
        payload.complaint_text,
        payload.location
    )

    routing = route(category, priority)

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
        raise HTTPException(status_code=404, detail="Complaint not found")

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
        raise HTTPException(status_code=404, detail="Complaint not found")

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


@router.get("/{complaint_id}/pdf")
def download_pdf(
    complaint_id: str,
    db: Session = Depends(get_db),
):
    complaint = db.query(Complaint).filter(
        Complaint.complaint_id == complaint_id
    ).first()

    if not complaint or not complaint.pdf_path:
        raise HTTPException(status_code=404, detail="PDF not found")

    pdf_file = Path(complaint.pdf_path)
    if not pdf_file.exists():
        raise HTTPException(status_code=404, detail="PDF file not found on disk")

    return FileResponse(
        str(pdf_file),
        media_type="application/pdf",
        filename=f"complaint_{complaint_id}.pdf",
    )


@router.post("/{complaint_id}/dispatch-email")
def dispatch_email(
    complaint_id: str,
    db: Session = Depends(get_db),
):
    complaint = db.query(Complaint).filter(
        Complaint.complaint_id == complaint_id
    ).first()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    subject = f"CivicAssist: Complaint {complaint_id} - {complaint.issue_category}"
    body = f"""
    <h2>Civic Complaint: {complaint.issue_category}</h2>
    <p><strong>Complaint ID:</strong> {complaint_id}</p>
    <p><strong>Citizen:</strong> {complaint.citizen_name}</p>
    <p><strong>Location:</strong> {complaint.location}</p>
    <p><strong>Priority:</strong> {complaint.priority}</p>
    <hr>
    <p>{complaint.complaint_text}</p>
    <hr>
    <p><strong>Generated Letter:</strong></p>
    <p>{complaint.generated_letter}</p>
    """

    success = send_email(
        receiver=complaint.department_email,
        subject=subject,
        body=body,
        pdf_path=complaint.pdf_path,
    )

    if success:
        complaint.email_sent = True
        db.commit()

    return {
        "message": "Email dispatched" if success else "Email dispatch failed",
        "complaint_id": complaint_id,
        "success": success,
    }