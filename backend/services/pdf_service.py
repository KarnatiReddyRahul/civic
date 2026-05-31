from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph
)

import os

os.makedirs(
    "generated_pdfs",
    exist_ok=True
)

def create_pdf(
    complaint_id,
    letter
):

    pdf_path = (
        f"generated_pdfs/{complaint_id}.pdf"
    )

    pdf = SimpleDocTemplate(pdf_path)

    pdf.build([
        Paragraph(letter)
    ])

    return pdf_path
