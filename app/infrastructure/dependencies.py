from typing import Dict, Any
import os

from app.infrastructure.messaging.rabbitmq_consumer import RabbitMQConsumer
from app.infrastructure.email.email_service import EmailService
from app.application.use_cases.send_email_notification import SendEmailNotificationUseCase


def build_container() -> Dict[str, Any]:
    """
    Build the dependency injection container.
    """
    email_service = EmailService(
        smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=os.getenv("SMTP_USER", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        from_email=os.getenv("SMTP_FROM_EMAIL", "noreply@videoprocessing.com"),
        from_name=os.getenv("SMTP_FROM_NAME", "Video Processing"),
    )

    send_email_notification_use_case = SendEmailNotificationUseCase(email_service)

    consumer = RabbitMQConsumer(
        rabbitmq_url=_build_rabbitmq_url(),
        send_email_use_case=send_email_notification_use_case,
    )

    return {
        "email_service": email_service,
        "send_email_notification_use_case": send_email_notification_use_case,
        "consumer": consumer,
    }


def _build_rabbitmq_url() -> str:
    user = os.getenv("RABBITMQ_USER", "guest")
    password = os.getenv("RABBITMQ_PASSWORD", "guest")
    host = os.getenv("RABBITMQ_HOST", "localhost")
    port = os.getenv("RABBITMQ_PORT", "5672")
    vhost = os.getenv("RABBITMQ_VHOST", "/")

    # Auto-detect SSL based on port: 5671 = SSL, 5672 = no SSL
    # Can be overridden with RABBITMQ_USE_SSL environment variable
    use_ssl = port == 5671
    protocol = "amqps" if use_ssl else "amqp"
    url = (
        f"{protocol}://{user}:{password}@{host}:{port}{vhost}"
    )
    
    return url
