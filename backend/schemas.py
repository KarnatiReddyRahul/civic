from pydantic import BaseModel

class ComplaintCreate(BaseModel):

    citizen_name: str

    email: str

    phone: str

    complaint_text: str

    location: str


class ComplaintResponse(BaseModel):

    complaint_id: str

    category: str

    department: str

    priority: str

    generated_letter: str