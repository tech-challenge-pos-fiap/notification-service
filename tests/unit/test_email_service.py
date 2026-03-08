from unittest.mock import AsyncMock, patch
import pytest
from app.infrastructure.email.email_service import EmailService


class TestEmailService:
    """Tests for EmailService"""

    @pytest.mark.asyncio
    async def test_send_email_success(self):
        """Should render template and send message via SMTP client."""
        # Arrange
        service = EmailService(
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_user="user",
            smtp_password="pass",
            from_email="noreply@example.com",
            from_name="Notifier",
        )

        smtp_client = AsyncMock()
        smtp_context_manager = AsyncMock()
        smtp_context_manager.__aenter__.return_value = smtp_client

        with patch(
            "app.infrastructure.email.email_service.get_email_template",
            return_value="<html>Hello</html>",
        ) as template_mock, patch(
            "app.infrastructure.email.email_service.aiosmtplib.SMTP",
            return_value=smtp_context_manager,
        ) as smtp_mock:
            # Act
            await service.send_email(
                recipient_email="to@example.com",
                template_name="verify_email",
                subject="Verify",
                context={"user_name": "Laura"},
            )

            # Assert
            template_mock.assert_called_once_with("verify_email", {"user_name": "Laura"})
            smtp_mock.assert_called_once_with(hostname="smtp.example.com", port=587)
            smtp_client.login.assert_awaited_once_with("user", "pass")
            smtp_client.send_message.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_send_email_raises_when_smtp_fails(self):
        """Should propagate SMTP errors."""
        # Arrange
        service = EmailService(
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_user="user",
            smtp_password="pass",
            from_email="noreply@example.com",
            from_name="Notifier",
        )

        smtp_client = AsyncMock()
        smtp_client.login.side_effect = Exception("SMTP unavailable")

        smtp_context_manager = AsyncMock()
        smtp_context_manager.__aenter__.return_value = smtp_client

        with patch(
            "app.infrastructure.email.email_service.get_email_template",
            return_value="<html>Hello</html>",
        ), patch(
            "app.infrastructure.email.email_service.aiosmtplib.SMTP",
            return_value=smtp_context_manager,
        ):
            # Act / Assert
            with pytest.raises(Exception, match="SMTP unavailable"):
                await service.send_email(
                    recipient_email="to@example.com",
                    template_name="verify_email",
                    subject="Verify",
                    context={"user_name": "Laura"},
                )

    @pytest.mark.asyncio
    async def test_send_email_uses_empty_context_when_none(self):
        """Should default context to empty dict when None."""
        service = EmailService(
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_user="user",
            smtp_password="pass",
            from_email="noreply@example.com",
            from_name="Notifier",
        )

        smtp_client = AsyncMock()
        smtp_context_manager = AsyncMock()
        smtp_context_manager.__aenter__.return_value = smtp_client

        with patch(
            "app.infrastructure.email.email_service.get_email_template",
            return_value="<html>Hello</html>",
        ) as template_mock, patch(
            "app.infrastructure.email.email_service.aiosmtplib.SMTP",
            return_value=smtp_context_manager,
        ):
            await service.send_email(
                recipient_email="to@example.com",
                template_name="verify_email",
                subject="Verify",
                context=None,
            )

        template_mock.assert_called_once_with("verify_email", {})
