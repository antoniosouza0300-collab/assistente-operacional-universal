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
    # Mapeia o nível de log configurado em settings
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Configura o logger base do Python
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Processadores compartilhados do structlog
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    # Seleciona o renderizador com base no ambiente ativo
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
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Retorna um logger estruturado configurado para o módulo especificado.
    
    Args:
        name (str): Nome do módulo ou componente (ex: __name__).
        
    Returns:
        structlog.stdlib.BoundLogger: Instância do logger estruturado.
    """
    return structlog.get_logger(name)
