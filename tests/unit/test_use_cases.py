import pytest
from unittest.mock import patch
from app.application.use_cases.send_email_notification import SendEmailNotificationUseCase
from app.domain.entities.notification import NotificationStatus


class TestSendEmailNotificationUseCase:
    """Tests for SendEmailNotificationUseCase"""
    
    @pytest.mark.asyncio
    async def test_send_email_successfully(
        self, send_email_use_case: SendEmailNotificationUseCase
    ):
        """Test sending email successfully"""

        user_id = 1
        email = "user@example.com"
        notification_type = "email_verification"
        template = "verify_email"
        subject = "Verify your email"
        data = {"verification_link": "https://example.com/verify"}

        result = await send_email_use_case.execute(
            user_id=user_id,
            recipient_email=email,
            notification_type=notification_type,
            template=template,
            subject=subject,
            data=data,
        )

        assert result.status == NotificationStatus.SENT
        assert result.user_id == user_id
        assert result.recipient_email == email
        assert result.error_message is None
    
    @pytest.mark.asyncio
    async def test_send_email_failure_with_retry(
        self, send_email_use_case: SendEmailNotificationUseCase
    ):
        """Test sending email with failure and retry"""

        send_email_use_case.email_service.send_email.side_effect = Exception(
            "SMTP connection failed"
        )

        result = await send_email_use_case.execute(
            user_id=1,
            recipient_email="user@example.com",
            notification_type="email_verification",
            template="verify_email",
            subject="Verify your email",
            data={},
        )

        assert result.status == NotificationStatus.RETRYING
        assert result.retry_count == 1
        assert "SMTP connection failed" in result.error_message
    
    @pytest.mark.asyncio
    async def test_send_email_max_retries_exceeded(
        self, send_email_use_case: SendEmailNotificationUseCase
    ):
        """Test repeated failures keep notification in retrying state"""
        # Arrange
        send_email_use_case.email_service.send_email.side_effect = Exception(
            "SMTP connection failed"
        )
        
        # Act - execute 4 times to exceed max retries (3)
        result = None
        for _ in range(4):
            result = await send_email_use_case.execute(
                user_id=1,
                recipient_email="user@example.com",
                notification_type="email_verification",
                template="verify_email",
                subject="Verify your email",
                data={},
            )
        
        # Assert
        assert result.status == NotificationStatus.RETRYING
        assert result.retry_count == 1
        assert send_email_use_case.email_service.send_email.await_count == 4

    @pytest.mark.asyncio
    async def test_send_email_with_data_none_defaults_to_empty_dict(
        self, send_email_use_case: SendEmailNotificationUseCase
    ):
        """Test that None data is converted to empty dict."""
        result = await send_email_use_case.execute(
            user_id=1,
            recipient_email="user@example.com",
            notification_type="email_verification",
            template="verify_email",
            subject="Verify your email",
            data=None,
        )

        assert result.status == NotificationStatus.SENT
        send_email_use_case.email_service.send_email.assert_awaited_once_with(
            recipient_email="user@example.com",
            template_name="verify_email",
            subject="Verify your email",
            context={},
        )

    @pytest.mark.asyncio
    async def test_send_email_failure_without_retry_marks_as_failed(
        self, send_email_use_case: SendEmailNotificationUseCase
    ):
        """Test failure path when retry is not allowed."""
        send_email_use_case.email_service.send_email.side_effect = Exception(
            "SMTP connection failed"
        )

        with patch(
            "app.application.use_cases.send_email_notification.Notification.can_retry",
            return_value=False,
        ):
            result = await send_email_use_case.execute(
                user_id=1,
                recipient_email="user@example.com",
                notification_type="email_verification",
                template="verify_email",
                subject="Verify your email",
                data={},
            )

        assert result.status == NotificationStatus.FAILED
        assert result.retry_count == 0
