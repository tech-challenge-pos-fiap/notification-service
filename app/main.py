import asyncio
import os
import logging
from dotenv import load_dotenv

from app.infrastructure.dependencies import build_container
from app.infrastructure.config.logging import configure_logging

load_dotenv()

logger = logging.getLogger(__name__)


async def main() -> None:
    configure_logging()
    logger.info("Starting Notification Service")
    container = build_container()
    consumer = container["consumer"]
    logger.info("Notification Service initialized and listening for events")

    await consumer.run_forever()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Notification Service stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        raise
