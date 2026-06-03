from pathlib import Path

from reportlab.platypus import Paragraph, SimpleDocTemplate

GENERATED_PDFS_DIR = Path(__file__).resolve().parent.parent / "generated_pdfs"
GENERATED_PDFS_DIR.mkdir(parents=True, exist_ok=True)

def create_pdf(
    complaint_id,
    letter
):

    pdf_path = GENERATED_PDFS_DIR / f"{complaint_id}.pdf"
    pdf = SimpleDocTemplate(str(pdf_path))

    pdf.build([
        Paragraph(letter)
    ])

    return str(pdf_path)
