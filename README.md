# Notification Service

A microservice responsible for sending email notifications within the video processing architecture.

## Overview

The Notification Service is an event-driven microservice that consumes notification events from RabbitMQ and sends emails to users. It's part of a distributed system architecture for video processing, handling all user communication needs such as job completion notifications, verification emails, and password resets.

## Features

- **Email Delivery:** Automated email notifications with templated content
- **RabbitMQ Consumer:** Event-driven architecture consuming notification events
- **Health & Readiness Checks:** Monitoring endpoints for container orchestration
- **Automatic Retry:** Failed message reprocessing with exponential backoff
- **Structured Logging:** JSON-formatted logs using structlog for better observability
- **Template System:** Flexible email templates for different notification types
- **Error Handling:** Robust error handling with dead-letter queue support

## Architecture

### Project Structure
```
notification-service/
├── app/
│   ├── application/          # Use cases and business logic
│   │   └── use_cases/        # Notification sending use cases
│   ├── domain/               # Domain entities and business rules
│   │   └── entities/         # Notification entity
│   ├── infrastructure/       # External integrations
│   │   ├── config/           # Configuration and settings
│   │   ├── email/            # Email service and templates
│   │   └── messaging/        # RabbitMQ consumer
│   └── main.py               # Application entry point
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   └── conftest.py           # Test fixtures
├── docker-compose.yml        # Local development setup
├── Dockerfile                # Container image definition
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Requirements

- **Python:** 3.11 or higher
- **Docker & Docker Compose:** For containerized deployment (optional)
- **RabbitMQ:** Message broker for event consumption
- **SMTP Server:** For sending emails (e.g., Gmail, SendGrid, AWS SES)

## Getting Started

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/

# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@yourapp.com

# Application Configuration
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Running with Docker Compose

The easiest way to run the service locally:

```bash
# Start all services (RabbitMQ + Notification Service)
docker compose up --build

# Run in detached mode
docker compose up -d --build

# View logs
docker compose logs -f notification-service

# Stop services
docker compose down
```

### Port Configuration

To avoid conflicts with other services, this project uses custom ports:

| Service | Default Port | Host Port | Environment Variable |
|---------|-------------|-----------|---------------------|
| RabbitMQ AMQP | 5672 | 5673 | `RABBITMQ_HOST_PORT` |
| RabbitMQ Management | 15672 | 15673 | `RABBITMQ_MANAGEMENT_HOST_PORT` |
| PostgreSQL | 5432 | 5434 | `POSTGRES_HOST_PORT` |

You can customize these ports in your `.env` file:

```env
RABBITMQ_HOST_PORT=5673
RABBITMQ_MANAGEMENT_HOST_PORT=15673
POSTGRES_HOST_PORT=5434
```

### Running Locally (without Docker)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the service
python -m app.main
```

## Usage

### Publishing Notification Events

Other services can publish notification events to RabbitMQ:

```python
import aio_pika
import json

# Connect to RabbitMQ
connection = await aio_pika.connect_robust("amqp://guest:guest@localhost:5672/")
channel = await connection.channel()

# Publish notification event
await channel.default_exchange.publish(
    aio_pika.Message(
        body=json.dumps({
            "user_id": 123,
            "email": "user@example.com",
            "notification_type": "email_verification",
            "template": "verify_email",
            "data": {
                "verification_link": "https://yourapp.com/verify?token=abc123",
                "user_name": "John Doe"
            }
        }).encode()
    ),
    routing_key="notifications"
)
```

### Notification Types

The service supports various notification types:

| Type | Description | Template Variables |
|------|-------------|-------------------|
| `email_verification` | Email address verification | `verification_link`, `user_name` |
| `password_reset` | Password reset request | `reset_link`, `user_name` |
| `job_completed` | Video processing completed | `job_id`, `download_link`, `user_name` |
| `job_failed` | Video processing failed | `job_id`, `error_message`, `user_name` |
| `welcome` | New user welcome email | `user_name`, `app_name` |

### Email Templates

Templates are defined in [`app/infrastructure/email/email_templates.py`](app/infrastructure/email/email_templates.py). Each template includes:

- **Subject:** Email subject line
- **Body:** HTML email content with variable placeholders
- **Variables:** Required data fields for template rendering

Example template:

```python
TEMPLATES = {
    "job_completed": {
        "subject": "Your video processing is complete!",
        "body": """
            <h2>Hello {user_name}!</h2>
            <p>Your video processing job #{job_id} has been completed successfully.</p>
            <p><a href="{download_link}">Download your processed video</a></p>
        """
    }
}
```

## Testing

### Run All Tests

```bash
# Run tests with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_email_service.py -v
```

### Test Coverage

The project maintains high test coverage:

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html
```

## Monitoring

### Health Checks

The service exposes health check endpoints (if implemented):

- **Liveness:** `/health` - Service is running
- **Readiness:** `/ready` - Service is ready to process messages

### Logging

Structured logs are output in JSON format for easy parsing:

```json
{
  "event": "notification_sent",
  "timestamp": "2024-03-13T10:30:00Z",
  "level": "info",
  "notification_type": "job_completed",
  "user_id": 123,
  "email": "user@example.com"
}
```

### Metrics

Key metrics to monitor:

- **Messages Processed:** Total notifications sent
- **Success Rate:** Percentage of successful deliveries
- **Retry Count:** Number of retried messages
- **Processing Time:** Average time to send notification
- **Dead Letter Queue:** Failed messages requiring attention

## Configuration

### Key Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `RABBITMQ_HOST` | RabbitMQ server hostname | `localhost` | Yes |
| `RABBITMQ_PORT` | RabbitMQ AMQP port | `5672` | Yes |
| `RABBITMQ_USER` | RabbitMQ username | `guest` | Yes |
| `RABBITMQ_PASSWORD` | RabbitMQ password | `guest` | Yes |
| `SMTP_HOST` | SMTP server hostname | - | Yes |
| `SMTP_PORT` | SMTP server port | `587` | Yes |
| `SMTP_USER` | SMTP username | - | Yes |
| `SMTP_PASSWORD` | SMTP password | - | Yes |
| `SMTP_FROM` | Default sender email | - | Yes |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `ENVIRONMENT` | Environment name | `development` | No |

### SMTP Configuration Examples

#### Gmail
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Use App Password, not regular password
```

#### SendGrid
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

#### AWS SES
```env
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your-ses-smtp-username
SMTP_PASSWORD=your-ses-smtp-password
```

## Deployment

### Docker

Build and run the container:

```bash
# Build image
docker build -t notification-service:latest .

# Run container
docker run -d \
  --name notification-service \
  --env-file .env \
  notification-service:latest
```

### AWS ECS

The service is designed to run on AWS ECS with:

- **Auto-scaling:** Based on RabbitMQ queue depth
- **Health checks:** Container health monitoring
- **Secrets:** Environment variables from AWS Secrets Manager
- **Logging:** CloudWatch Logs integration

## Troubleshooting

### Common Issues

**Issue:** Emails not being sent
- Check SMTP credentials and configuration
- Verify SMTP server allows connections from your IP
- Check firewall rules for SMTP port (usually 587 or 465)

**Issue:** Messages not being consumed
- Verify RabbitMQ connection settings
- Check queue exists and has messages
- Review consumer logs for errors

**Issue:** High retry rate
- Check SMTP server rate limits
- Verify email addresses are valid
- Review error logs for specific failures

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is part of the FIAP video processing system.

## Support

For issues and questions:
- Create an issue in the repository
- Contact the development team
- Check the project documentation
