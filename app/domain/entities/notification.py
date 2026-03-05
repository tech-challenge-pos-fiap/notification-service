from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from enum import Enum


class NotificationType(str, Enum):
    """Types of notifications"""
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    JOB_COMPLETED = "job_completed"
    JOB_FAILED = "job_failed"
    WELCOME = "welcome"


class NotificationStatus(str, Enum):
    """Status of notification delivery"""
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class Notification:
    id: str
    user_id: int
    recipient_email: str
    notification_type: NotificationType
    template: str
    subject: str
    data: Dict[str, Any]
    status: NotificationStatus = NotificationStatus.PENDING
    retry_count: int = 0
    created_at: datetime = None
    updated_at: datetime = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = datetime.now(timezone.utc)
    
    def mark_as_sent(self) -> None:
        self.status = NotificationStatus.SENT
        self.updated_at = datetime.now(timezone.utc)
        self.error_message = None
    
    def mark_as_failed(self, error_message: str) -> None:
        self.status = NotificationStatus.FAILED
        self.updated_at = datetime.now(timezone.utc)
        self.error_message = error_message
    
    def mark_for_retry(self) -> None:
        self.status = NotificationStatus.RETRYING
        self.retry_count += 1
        self.updated_at = datetime.now(timezone.utc)
    
    def can_retry(self, max_retries: int = 3) -> bool:
        return self.retry_count < max_retries
