"""
Testes Unitários para o Sistema de Logging Estruturado - Assistente Operacional Universal
Valida a configuração do structlog para os ambientes de desenvolvimento e produção.
"""

import structlog
import pytest
from core.logging import configure_logging, get_logger


def test_configure_logging_development():
    """Valida se a configuração de logging inicializa o structlog corretamente em desenvolvimento."""
    configure_logging()
    logger = get_logger("test_module_dev")
    
    assert logger is not None
    assert isinstance(logger, structlog.stdlib.BoundLogger)


def test_configure_logging_production(monkeypatch):
    """Valida a configuração de logging no ambiente de produção (com JSONRenderer)."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    
    configure_logging()
    logger = get_logger("test_module_prod")
    
    assert logger is not None
    assert isinstance(logger, structlog.stdlib.BoundLogger)
