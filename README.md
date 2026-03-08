# Notification Service

Microserviço responsável pelo envio de notificações por e-mail dentro da arquitetura de processamento de vídeos.

## Funcionalidades

- **Envio de e-mail:** disparo de notificações por e-mail.
- **Consumidor RabbitMQ:** processamento de eventos de notificação.
- **Health check & readiness:** endpoints para monitoramento.
- **Retry automático:** reprocessamento de mensagens com falha.
- **Logs estruturados:** logs em formato estruturado (structlog).

## Estrutura do projeto
```
app/
├── application/      # casos de uso (use_cases)
├── domain/           # entidades e regras de negócio
├── infrastructure/   # integrações (email, messaging, config)
├── main.py           # ponto de entrada
```

## Requisitos
- Python 3.11+
- Docker & Docker Compose (opcional)
- RabbitMQ (para execução local/integrada)

## Executar com Docker Compose
Crie um arquivo de variáveis de ambiente conforme sua infraestrutura (p.ex. copie e ajuste `.env.example` se presente).
```bash
docker compose up --build
```

### Portas no host (evitar conflito local)
Por padrão, este projeto expõe no host:

- RabbitMQ AMQP: `5673`
- RabbitMQ Management: `15673`
- Postgres: `5434`

Se quiser mudar, defina no `.env`:

```env
RABBITMQ_HOST_PORT=5673
RABBITMQ_MANAGEMENT_HOST_PORT=15673
POSTGRES_HOST_PORT=5434
```

## Uso (exemplo de publicação de evento)

```python
await messaging_gateway.publish(
    exchange="notifications",
    routing_key="user.verification.email",
    message={
        "user_id": 123,
        "email": "user@example.com",
        "notification_type": "email_verification",
        "template": "verify_email",
        "data": {"verification_link": "https://..."},
    },
)
```

## Tipos de notificação (exemplos)

- `email_verification`
- `password_reset`
- `job_completed`
- `job_failed`
- `welcome`

## Endpoints

- `GET /health` — status da aplicação

## Testes
para rodar os testes:
```bash
pytest -v
```
para cobertura de código:
```bash
pytest --cov
```
## Variáveis importantes

- `RABBITMQ_HOST` — host do RabbitMQ
- `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` — configurações SMTP
