"""
Conector DSPy - Assistente Operacional Universal
Gerencia a inicialização e execução de módulos, programas e preditores baseados em DSPy.
"""

import logging
from typing import Any, Dict, Optional

from integrations.base import BaseIntegration, IntegrationError

logger = logging.getLogger(__name__)


class DSPyIntegration(BaseIntegration):
    """
    Conector para integração com DSPy.
    Encapsula a execução de programas ou preditores compilados em DSPy.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.program: Any = None

    def initialize(self) -> None:
        """
        Inicializa o conector recebendo o programa ou módulo DSPy via config.
        """
        self.program = self.config.get("program")
        if not self.program:
            raise IntegrationError("Nenhum programa ou módulo DSPy válido foi fornecido na configuração.")
        
        self._is_initialized = True
        logger.info("DSPyIntegration inicializada com sucesso.")

    def health_check(self) -> bool:
        """Verifica se o programa está instanciado e operacional."""
        self._validate_initialization()
        return self.program is not None

    def execute(self, **kwargs: Any) -> Any:
        """
        Executa o programa ou preditor DSPy com os argumentos fornecidos.
        
        Args:
            **kwargs: Argumentos nomeados exigidos pelo programa/preditor DSPy.
            
        Returns:
            Any: Resultado estruturado retornado pelo DSPy.
        """
        self._validate_initialization()
        try:
            logger.info("Executando programa DSPy...")
            result = self.program(**kwargs)
            return result
        except Exception as e:
            logger.error("Erro durante a execução do programa DSPy: %s", str(e))
            raise IntegrationError(f"Falha na execução do DSPy: {e}") from e
