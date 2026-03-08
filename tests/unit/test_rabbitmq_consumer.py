import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.infrastructure.messaging.rabbitmq_consumer import RabbitMQConsumer


class _MessageProcessContext:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False


class TestRabbitMQConsumer:
    """Tests for RabbitMQConsumer"""

    @pytest.mark.asyncio
    async def test_handle_notification_event_calls_use_case(self):
        """Should call use case when event is valid."""
        use_case = MagicMock()
        use_case.execute = AsyncMock()
        consumer = RabbitMQConsumer("amqp://guest:guest@localhost:5672/", use_case)

        event = {
            "notification_type": "email_verification",
            "user_id": 1,
            "email": "user@example.com",
            "template": "verify_email",
            "subject": "Verify your email",
            "data": {"verification_link": "https://example.com"},
        }

        await consumer._handle_notification_event(event)

        use_case.execute.assert_awaited_once_with(
            user_id=1,
            recipient_email="user@example.com",
            notification_type="email_verification",
            template="verify_email",
            subject="Verify your email",
            data={"verification_link": "https://example.com"},
        )

    @pytest.mark.asyncio
    async def test_handle_notification_event_missing_fields_does_not_call_use_case(self):
        """Should skip invalid events."""
        use_case = MagicMock()
        use_case.execute = AsyncMock()
        consumer = RabbitMQConsumer("amqp://guest:guest@localhost:5672/", use_case)

        event = {
            "notification_type": "email_verification",
            "user_id": 1,
            "email": "user@example.com",
            "template": "verify_email",
            "data": {},
        }
        await consumer._handle_notification_event(event)

        use_case.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_message_invalid_json_nacks_message(self):
        """Should nack message when payload is invalid JSON."""
        use_case = MagicMock()
        use_case.execute = AsyncMock()
        consumer = RabbitMQConsumer("amqp://guest:guest@localhost:5672/", use_case)

        message = MagicMock()
        message.body = b"{invalid-json}"
        message.routing_key = "user.verification.email"
        message.nack = AsyncMock()
        message.process.return_value = _MessageProcessContext()

        await consumer._process_message(message)

        message.nack.assert_awaited_once_with(requeue=True)
        use_case.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Should connect and declare exchange successfully."""
        use_case = MagicMock()
        use_case.execute = AsyncMock()
        consumer = RabbitMQConsumer("amqp://guest:guest@localhost:5672/", use_case)

        connection = AsyncMock()
        channel = AsyncMock()
        exchange = AsyncMock()
        connection.channel.return_value = channel
        channel.declare_exchange.return_value = exchange

        with patch(
            "app.infrastructure.messaging.rabbitmq_consumer.aio_pika.connect_robust",
            new=AsyncMock(return_value=connection),
        ) as connect_mock:
            await consumer.connect()

        connect_mock.assert_awaited_once_with("amqp://guest:guest@localhost:5672/")
        channel.declare_exchange.assert_awaited_once()
        assert consumer.connection is connection
        assert consumer.channel is channel
        assert consumer.exchange is exchange

    @pytest.mark.asyncio
    async def test_connect_raises_on_failure(self):
        """Should propagate connection errors."""
        use_case = MagicMock()
        use_case.execute = AsyncMock()
        consumer = RabbitMQConsumer("amqp://guest:guest@localhost:5672/", use_case)

        with patch(
            "app.infrastructure.messaging.rabbitmq_consumer.aio_pika.connect_robust",
            new=AsyncMock(side_effect=Exception("RabbitMQ down")),
        ):
            with pytest.raises(Exception, match="RabbitMQ down"):
                await consumer.connect()

    @pytest.mark.asyncio
    async def test_declare_queues_requires_connection(self):
        """Should fail when channel/exchange are missing."""
        use_case = MagicMock()
        use_case.execute = AsyncMock()
        consumer = RabbitMQConsumer("amqp://guest:guest@localhost:5672/", use_case)

        with pytest.raises(RuntimeError, match="Not connected to RabbitMQ"):
            await consumer.declare_queues()

    @pytest.mark.asyncio
    async def test_declare_queues_binds_routing_keys_and_consumes(self):
        """Should bind all routing keys and register consumer callback."""
        use_case = MagicMock()
        use_case.execute = AsyncMock()
        consumer = RabbitMQConsumer("amqp://guest:guest@localhost:5672/", use_case)

        channel = AsyncMock()
        exchange = MagicMock()
        email_queue = AsyncMock()
        channel.declare_queue.return_value = email_queue
        consumer.channel = channel
        consumer.exchange = exchange

        await consumer.declare_queues()

        channel.declare_queue.assert_awaited_once_with(
            name="notifications.email",
            durable=True,
        )
        assert email_queue.bind.await_count == 5
        email_queue.consume.assert_awaited_once_with(consumer._process_message)

    @pytest.mark.asyncio
    async def test_process_message_unexpected_error_nacks_message(self):
        """Should nack message when handler raises unexpected error."""
        use_case = MagicMock()
        use_case.execute = AsyncMock()
        consumer = RabbitMQConsumer("amqp://guest:guest@localhost:5672/", use_case)
        consumer._handle_notification_event = AsyncMock(side_effect=Exception("boom"))

        message = MagicMock()
        message.body = b'{"notification_type":"email_verification"}'
        message.routing_key = "user.verification.email"
        message.nack = AsyncMock()
        message.process.return_value = _MessageProcessContext()

        await consumer._process_message(message)

        message.nack.assert_awaited_once_with(requeue=True)

    @pytest.mark.asyncio
    async def test_run_forever_calls_connect_declare_and_disconnect(self):
        """Should always disconnect in run_forever lifecycle."""
        use_case = MagicMock()
        use_case.execute = AsyncMock()
        consumer = RabbitMQConsumer("amqp://guest:guest@localhost:5672/", use_case)

        consumer.connect = AsyncMock()
        consumer.declare_queues = AsyncMock()
        consumer.disconnect = AsyncMock()

        event = MagicMock()
        event.wait = AsyncMock(return_value=None)

        with patch("app.infrastructure.messaging.rabbitmq_consumer.asyncio.Event", return_value=event):
            await consumer.run_forever()

        consumer.connect.assert_awaited_once()
        consumer.declare_queues.assert_awaited_once()
        consumer.disconnect.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_run_forever_raises_and_still_disconnects(self):
        """Should re-raise run_forever errors and disconnect."""
        use_case = MagicMock()
        use_case.execute = AsyncMock()
        consumer = RabbitMQConsumer("amqp://guest:guest@localhost:5672/", use_case)

        consumer.connect = AsyncMock(side_effect=Exception("fatal"))
        consumer.disconnect = AsyncMock()

        with pytest.raises(Exception, match="fatal"):
            await consumer.run_forever()

        consumer.disconnect.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_disconnect_with_connection_closes_it(self):
        """Should close RabbitMQ connection when present."""
        use_case = MagicMock()
        use_case.execute = AsyncMock()
        consumer = RabbitMQConsumer("amqp://guest:guest@localhost:5672/", use_case)

        consumer.connection = AsyncMock()
        await consumer.disconnect()

        consumer.connection.close.assert_awaited_once()
