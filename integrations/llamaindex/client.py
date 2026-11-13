"""
Conector LlamaIndex - Assistente Operacional Universal
Gerencia a inicialização e execução de consultas em índices e query engines do LlamaIndex.
"""

import logging
from typing import Any, Dict, Optional

from integrations.base import BaseIntegration, IntegrationError

logger = logging.getLogger(__name__)


class LlamaIndexIntegration(BaseIntegration):
    """
    Conector para integração com LlamaIndex.
    Encapsula a execução de consultas em motores de busca (Query Engines) e índices.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.query_engine: Any = None

    def initialize(self) -> None:
        """
        Inicializa o conector recebendo o query_engine ou índice via config.
        """
        self.query_engine = self.config.get("query_engine")
        if not self.query_engine:
            raise IntegrationError("Nenhum query_engine ou índice LlamaIndex válido foi fornecido na configuração.")
        
        self._is_initialized = True
        logger.info("LlamaIndexIntegration inicializada com sucesso.")

    def health_check(self) -> bool:
        """Verifica se o query_engine está instanciado e operacional."""
        self._validate_initialization()
        return self.query_engine is not None

    def execute(self, query_str: str, **kwargs: Any) -> Any:
        """
        Executa uma consulta (query) no motor do LlamaIndex.
        
        Args:
            query_str (str): Texto da consulta ou pergunta a ser feita ao índice.
            **kwargs: Parâmetros adicionais para o método query.
            
        Returns:
            Any: Resposta estruturada retornada pelo LlamaIndex.
        """
        self._validate_initialization()
        try:
            logger.info("Executando consulta no LlamaIndex...")
            result = self.query_engine.query(query_str, **kwargs)
            return result
        except Exception as e:
            logger.error("Erro durante a execução da consulta no LlamaIndex: %s", str(e))
            raise IntegrationError(f"Falha na execução do LlamaIndex: {e}") from e
