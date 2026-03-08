"""
Tests conftest - Shared fixtures and configuration
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.infrastructure.email.email_service import EmailService
from app.application.use_cases.send_email_notification import SendEmailNotificationUseCase


@pytest.fixture
def mock_email_service() -> AsyncMock:
    """Create a mock email service"""
    return AsyncMock(spec=EmailService)


@pytest.fixture
def send_email_use_case(mock_email_service: AsyncMock) -> SendEmailNotificationUseCase:
    """Create a send email use case with mock service"""
    return SendEmailNotificationUseCase(email_service=mock_email_service)
