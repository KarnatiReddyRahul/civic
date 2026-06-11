import logging
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

logger = logging.getLogger(__name__)


def send_email(
    receiver: str,
    subject: str,
    body: str,
    pdf_path: str | None = None,
) -> bool:
    smtp_host = os.environ.get("SMTP_HOST", "")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASSWORD", "")
    smtp_from = os.environ.get("SMTP_FROM", "noreply@civicassist.ai")

    if not smtp_host or not smtp_user:
        logger.info(f"SMTP not configured. Would send email to {receiver}: {subject}")
        return True

    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_from
        msg["To"] = receiver
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        if pdf_path and Path(pdf_path).exists():
            with open(pdf_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={Path(pdf_path).name}",
            )
            msg.attach(part)

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        logger.info(f"Email sent to {receiver}")
        return True

    except Exception as e:
        logger.warning(f"Failed to send email to {receiver}: {e}")
        return False
