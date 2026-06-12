import uuid
from pathlib import Path
from datetime import datetime

from backend.database import SessionLocal
from backend.models import Complaint
from backend.services.ai_classifier import classify
from backend.services.ai_generator import generate_letter
from backend.services.pdf_service import create_pdf
from backend.services.router_service import route
from backend.services.email_service import send_email


def get_all_complaints():
    db = SessionLocal()
    try:
        complaints = db.query(Complaint).all()
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
                "created_at": str(c.created_at) if c.created_at else "",
                "updated_at": str(c.updated_at) if c.updated_at else "",
            })
        return result
    finally:
        db.close()


def get_complaint_by_id(complaint_id: str):
    db = SessionLocal()
    try:
        c = db.query(Complaint).filter(Complaint.complaint_id == complaint_id).first()
        if not c:
            return None
        return {
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
            "created_at": str(c.created_at) if c.created_at else "",
            "updated_at": str(c.updated_at) if c.updated_at else "",
        }
    finally:
        db.close()


def submit_complaint(
    citizen_name: str,
    email: str,
    phone: str,
    complaint_text: str,
    location: str,
    latitude: float | None = None,
    longitude: float | None = None,
):
    category, priority = classify(complaint_text, location)
    routing = route(category, priority)
    complaint_id = str(uuid.uuid4())[:8]

    letter = generate_letter(category, location, complaint_text)
    pdf_path = create_pdf(complaint_id, letter)

    db = SessionLocal()
    try:
        complaint = Complaint(
            complaint_id=complaint_id,
            citizen_name=citizen_name,
            email=email,
            phone=phone,
            complaint_text=complaint_text,
            issue_category=category,
            department=routing["department"],
            department_email=routing["email"],
            priority=routing["priority"],
            location=location,
            latitude=latitude,
            longitude=longitude,
            generated_letter=letter,
            status="Submitted",
            email_sent=False,
            pdf_path=pdf_path,
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        return {
            "complaint_id": complaint_id,
            "category": category,
            "department": routing["department"],
            "priority": routing["priority"],
            "generated_letter": letter,
        }
    finally:
        db.close()


def update_complaint_status(complaint_id: str, new_status: str):
    db = SessionLocal()
    try:
        complaint = db.query(Complaint).filter(Complaint.complaint_id == complaint_id).first()
        if not complaint:
            return None
        complaint.status = new_status
        db.commit()
        return {"message": "Status updated successfully", "complaint_id": complaint_id, "new_status": new_status}
    finally:
        db.close()


def get_pdf_path(complaint_id: str):
    db = SessionLocal()
    try:
        complaint = db.query(Complaint).filter(Complaint.complaint_id == complaint_id).first()
        if not complaint or not complaint.pdf_path:
            return None
        pdf_file = Path(complaint.pdf_path)
        return str(pdf_file) if pdf_file.exists() else None
    finally:
        db.close()


def dispatch_email(complaint_id: str):
    db = SessionLocal()
    try:
        complaint = db.query(Complaint).filter(Complaint.complaint_id == complaint_id).first()
        if not complaint:
            return {"message": "Complaint not found", "success": False}

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

        return {"message": "Email dispatched" if success else "Email dispatch failed", "complaint_id": complaint_id, "success": success}
    finally:
        db.close()


def get_dashboard_stats():
    db = SessionLocal()
    try:
        total = db.query(Complaint).count()
        resolved = db.query(Complaint).filter(Complaint.status == "Resolved").count()
        pending = db.query(Complaint).filter(Complaint.status != "Resolved").count()
        high_priority = db.query(Complaint).filter(Complaint.priority == "High").count()
        return {
            "total_complaints": total,
            "resolved": resolved,
            "pending": pending,
            "high_priority": high_priority,
        }
    finally:
        db.close()
