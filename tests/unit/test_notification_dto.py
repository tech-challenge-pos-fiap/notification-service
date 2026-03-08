import pytest

from pydantic import ValidationError

from app.application.dtos.notification_dto import (
    NotificationTypeDTO,
    SendNotificationRequestDTO,
    NotificationResponseDTO,
)


class TestNotificationDTOs:
    def test_send_notification_request_dto_valid(self):
        dto = SendNotificationRequestDTO(
            user_id=1,
            recipient_email="user@example.com",
            notification_type=NotificationTypeDTO.EMAIL_VERIFICATION,
            template="verify_email",
            subject="Verify",
            data={"a": 1},
        )

        assert dto.user_id == 1
        assert dto.recipient_email == "user@example.com"
        assert dto.notification_type == NotificationTypeDTO.EMAIL_VERIFICATION
        assert dto.data == {"a": 1}

    def test_send_notification_request_dto_defaults_data(self):
        dto = SendNotificationRequestDTO(
            user_id=1,
            recipient_email="user@example.com",
            notification_type=NotificationTypeDTO.WELCOME,
            template="welcome",
            subject="Welcome",
        )

        assert dto.data == {}

    def test_send_notification_request_dto_invalid_email(self):
        with pytest.raises(ValidationError):
            SendNotificationRequestDTO(
                user_id=1,
                recipient_email="not-an-email",
                notification_type=NotificationTypeDTO.WELCOME,
                template="welcome",
                subject="Welcome",
            )

    def test_notification_response_dto(self):
        dto = NotificationResponseDTO(id="123", status="sent", message="ok")

        assert dto.id == "123"
        assert dto.status == "sent"
        assert dto.message == "ok"
