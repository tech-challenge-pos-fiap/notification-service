from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, Dict, Any
from enum import Enum


class NotificationTypeDTO(str, Enum):
    """Types of notifications"""
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    JOB_COMPLETED = "job_completed"
    JOB_FAILED = "job_failed"
    WELCOME = "welcome"


class SendNotificationRequestDTO(BaseModel):
    user_id: int = Field(..., description="User ID")
    recipient_email: EmailStr = Field(..., description="Recipient email address")
    notification_type: NotificationTypeDTO = Field(..., description="Type of notification")
    template: str = Field(..., description="Email template name")
    subject: str = Field(..., description="Email subject")
    data: Dict[str, Any] = Field(default_factory=dict, description="Template variables")
    
    model_config = ConfigDict(use_enum_values=True)


class NotificationResponseDTO(BaseModel):
    id: str
    status: str
    message: Optional[str] = None
    
    model_config = ConfigDict(use_enum_values=True)
