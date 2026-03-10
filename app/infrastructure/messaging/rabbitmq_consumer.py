import asyncio
import json
import logging

from typing import Optional, Dict, Any

import aio_pika

from app.application.use_cases.send_email_notification import SendEmailNotificationUseCase

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    """
    RabbitMQ consumer
    """
    
    def __init__(
        self,
        rabbitmq_url: str,
        send_email_use_case: SendEmailNotificationUseCase,
    ):
        self.rabbitmq_url = rabbitmq_url
        self.send_email_use_case = send_email_use_case
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None
    
    async def connect(self) -> None:
        """
        Establish connection to RabbitMQ.
        """
        try:
            logger.info("Connecting to RabbitMQ...")
            self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self.channel = await self.connection.channel()
            self.exchange = await self.channel.declare_exchange(
                name="notifications",
                type=aio_pika.ExchangeType.TOPIC,
                durable=True,
            )
            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise
    
    async def declare_queues(self) -> None:
        if not self.channel or not self.exchange:
            raise RuntimeError("Not connected to RabbitMQ. Call connect() first.")

        email_queue = await self.channel.declare_queue(
            name="notifications.email",
            durable=True,
        )
        
        routing_keys = [
            "user.verification.email",
            "user.password_reset.email",
            "job.completed.email",
            "job.failed.email",
            "user.welcome.email",
        ]
        
        for routing_key in routing_keys:
            await email_queue.bind(self.exchange, routing_key=routing_key)
            logger.info(f"Bound queue to routing key: {routing_key}")

        await email_queue.consume(self._process_message)
        logger.info("Queue declared and consumer started")
    
    async def _process_message(self, message: aio_pika.IncomingMessage) -> None:
        """
        Process a message from the queue.
        """
        try:
            body = json.loads(message.body.decode())
            logger.info(
                f"Received message: {message.routing_key}",
                extra={"routing_key": message.routing_key},
            )
            await self._handle_notification_event(body)
            await message.ack()
            
        except json.JSONDecodeError as e:
            logger.error(
                f"Failed to parse message: {str(e)}",
                exc_info=True,
            )
            await message.reject(requeue=False)
        except Exception as e:
            logger.error(
                f"Error processing message: {str(e)}",
                exc_info=True,
            )
            await message.nack(requeue=True)
    
    async def _handle_notification_event(self, event: Dict[str, Any]) -> None:
        """
        Handle a notification event.
        """
        notification_type = event.get("notification_type")
        user_id = event.get("user_id")
        email = event.get("email")
        template = event.get("template")
        subject = event.get("subject")
        data = event.get("data", {})
        
        if not all([notification_type, user_id, email, template, subject]):
            logger.error(
                "Missing required fields in notification event",
                extra={"event": event},
            )
            return

        await self.send_email_use_case.execute(
            user_id=user_id,
            recipient_email=email,
            notification_type=notification_type,
            template=template,
            subject=subject,
            data=data,
        )
    
    async def run_forever(self) -> None:
        """
        Run the consumer indefinitely.
        """
        try:
            await self.connect()
            await self.declare_queues()
            logger.info("Notification consumer is running...")
            await asyncio.Event().wait()
        except Exception as e:
            logger.error(f"Consumer error: {str(e)}", exc_info=True)
            raise
        finally:
            await self.disconnect()
    
    async def disconnect(self) -> None:
        """
        Disconnect from RabbitMQ.
        """
        if self.connection:
            logger.info("Disconnecting from RabbitMQ...")
            await self.connection.close()
            logger.info("Disconnected from RabbitMQ")
