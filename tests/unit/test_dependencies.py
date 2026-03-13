from unittest.mock import MagicMock, patch
from app.infrastructure.dependencies import build_container, _build_rabbitmq_url


class TestDependencies:
    def test_build_rabbitmq_url_defaults(self, monkeypatch):
        for key in [
            "RABBITMQ_USER",
            "RABBITMQ_PASSWORD",
            "RABBITMQ_HOST",
            "RABBITMQ_PORT",
            "RABBITMQ_VHOST",
        ]:
            monkeypatch.delenv(key, raising=False)

        assert _build_rabbitmq_url() == "amqp://guest:guest@localhost:5672/"

    def test_build_rabbitmq_url_from_env(self, monkeypatch):
        monkeypatch.setenv("RABBITMQ_USER", "u")
        monkeypatch.setenv("RABBITMQ_PASSWORD", "p")
        monkeypatch.setenv("RABBITMQ_HOST", "rabbit")
        monkeypatch.setenv("RABBITMQ_PORT", "5673")
        monkeypatch.setenv("RABBITMQ_VHOST", "v1")

        assert _build_rabbitmq_url() == "amqp://u:p@rabbit:5673v1"

    def test_build_container_wires_dependencies(self, monkeypatch):
        monkeypatch.setenv("SMTP_HOST", "smtp.test")
        monkeypatch.setenv("SMTP_PORT", "2525")
        monkeypatch.setenv("SMTP_USER", "user")
        monkeypatch.setenv("SMTP_PASSWORD", "pass")
        monkeypatch.setenv("SMTP_FROM_EMAIL", "noreply@test.com")
        monkeypatch.setenv("SMTP_FROM_NAME", "Notify")

        email_service_instance = MagicMock(name="email_service")
        use_case_instance = MagicMock(name="use_case")
        consumer_instance = MagicMock(name="consumer")

        with patch(
            "app.infrastructure.dependencies.EmailService",
            return_value=email_service_instance,
        ) as email_cls, patch(
            "app.infrastructure.dependencies.SendEmailNotificationUseCase",
            return_value=use_case_instance,
        ) as use_case_cls, patch(
            "app.infrastructure.dependencies.RabbitMQConsumer",
            return_value=consumer_instance,
        ) as consumer_cls, patch(
            "app.infrastructure.dependencies._build_rabbitmq_url",
            return_value="amqp://custom",
        ):
            container = build_container()

        email_cls.assert_called_once_with(
            smtp_host="smtp.test",
            smtp_port=2525,
            smtp_user="user",
            smtp_password="pass",
            from_email="noreply@test.com",
            from_name="Notify",
        )
        use_case_cls.assert_called_once_with(email_service_instance)
        consumer_cls.assert_called_once_with(
            rabbitmq_url="amqp://custom",
            send_email_use_case=use_case_instance,
        )

        assert container["email_service"] is email_service_instance
        assert container["send_email_notification_use_case"] is use_case_instance
        assert container["consumer"] is consumer_instance
