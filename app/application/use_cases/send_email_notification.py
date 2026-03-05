import logging
from typing import Optional, Dict, Any
import uuid

from app.domain.entities.notification import (
    Notification,
    NotificationType,
)
from app.infrastructure.email.email_service import EmailService

logger = logging.getLogger(__name__)


class SendEmailNotificationUseCase:
    """
    Use case for sending email notifications.
    """
    
    def __init__(self, email_service: EmailService):
        self.email_service = email_service
    
    async def execute(
        self,
        user_id: int,
        recipient_email: str,
        notification_type: str,
        template: str,
        subject: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        if data is None:
            data = {}

        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            recipient_email=recipient_email,
            notification_type=NotificationType(notification_type),
            template=template,
            subject=subject,
            data=data,
        )
        
        logger.info(
            f"Sending {notification_type} notification to {recipient_email}",
            extra={"user_id": user_id, "notification_id": notification.id},
        )
        
        try:
            await self.email_service.send_email(
                recipient_email=recipient_email,
                template_name=template,
                subject=subject,
                context=data,
            )

            notification.mark_as_sent()
            logger.info(
                f"Notification sent successfully",
                extra={"notification_id": notification.id},
            )
            
        except Exception as e:
            logger.error(
                f"Failed to send notification: {str(e)}",
                extra={
                    "notification_id": notification.id,
                    "error": str(e),
                },
                exc_info=True,
            )

            notification.mark_as_failed(str(e))
            if notification.can_retry():
                notification.mark_for_retry()
                logger.info(
                    f"Notification marked for retry",
                    extra={
                        "notification_id": notification.id,
                        "retry_count": notification.retry_count,
                    },
                )
            else:
                logger.error(
                    f"Max retries reached for notification",
                    extra={"notification_id": notification.id},
                )
        
        return notification
