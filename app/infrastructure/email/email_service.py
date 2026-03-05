import logging
from typing import Optional, Dict, Any

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.infrastructure.email.email_templates import get_email_template

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending emails via SMTP.
    """
    
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_email: str,
        from_name: str,
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.from_name = from_name
    
    async def send_email(
        self,
        recipient_email: str,
        template_name: str,
        subject: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Send an email using a template.
        """
        if context is None:
            context = {}
        
        try:
            html_content = get_email_template(template_name, context)

            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = recipient_email

            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
            ) as smtp:
                await smtp.login(self.smtp_user, self.smtp_password)
                await smtp.send_message(message)
            
            logger.info(f"Email sent to {recipient_email}")
        
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}", exc_info=True)
            raise
