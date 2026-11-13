"""
Sistema de Logging Estruturado (Core) - Assistente Operacional Universal
Configura o structlog para logging unificado com suporte a JSON (produção) e console (desenvolvimento).
"""

import logging
import sys
import structlog
from config.settings import settings


def configure_logging() -> None:
    """
    Configura o logging global da aplicação utilizando structlog e a biblioteca padrão Python.
    """
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if settings.environment.lower() == "production":
        processors = shared_processors + [
            structlog.processors.JSONRenderer()
        ]
    else:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Retorna um logger estruturado configurado para o módulo especificado.
    """
    return structlog.stdlib.get_logger(name).blind()
