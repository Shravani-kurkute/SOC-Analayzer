from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from app.core.config import settings
from app.database.session import engine
from app.database.redis import redis_client

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info(
        "Starting SentinelAI",
        environment=settings.ENVIRONMENT,
        version=settings.VERSION,
    )

    try:
        async with engine.connect() as conn:
            await conn.exec_driver_sql("SELECT 1")
            logger.info("Database connection established")
    except Exception as e:
        logger.error("Database connection failed", error=str(e))
        raise

    try:
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning("Redis connection failed, running without cache", error=str(e))

    yield

    logger.info("Shutting down SentinelAI")

    await engine.dispose()
    await redis_client.close()
