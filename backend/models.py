from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Complaint(Base):

    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True)

    complaint_id = Column(String, unique=True)

    citizen_name = Column(String)

    email = Column(String)

    phone = Column(String)

    issue_category = Column(String)

    complaint_text = Column(String)

    generated_letter = Column(String)

    department = Column(String)

    department_email = Column(String)

    priority = Column(String)

    location = Column(String)

    latitude = Column(Float)

    longitude = Column(Float)

    status = Column(String)

    email_sent = Column(Boolean)

    pdf_path = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow
    )