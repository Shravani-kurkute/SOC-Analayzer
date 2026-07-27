import logging
import sys

import structlog


def setup_logging() -> None:
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ],
        ),
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    log_renderer = structlog.dev.ConsoleRenderer() if sys.stderr.isatty() else structlog.processors.JSONRenderer()

    handler = logging.StreamHandler()
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                log_renderer,
            ],
        ),
    )

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    for log_name in ["uvicorn", "uvicorn.access", "fastapi"]:
        logging.getLogger(log_name).handlers.clear()
        logging.getLogger(log_name).propagate = True

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
