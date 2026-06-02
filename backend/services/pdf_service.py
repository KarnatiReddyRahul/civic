from pathlib import Path
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph
)

GENERATED_PDFS_DIR = Path(__file__).resolve().parent.parent / "generated_pdfs"
GENERATED_PDFS_DIR.mkdir(parents=True, exist_ok=True)

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
