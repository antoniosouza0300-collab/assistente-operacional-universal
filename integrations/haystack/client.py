"""
Conector Haystack - Assistente Operacional Universal
Gerencia a inicialização e execução de pipelines do Deepset Haystack.
"""

import logging
from typing import Any, Dict, Optional

from integrations.base import BaseIntegration, IntegrationError

logger = logging.getLogger(__name__)


class HaystackIntegration(BaseIntegration):
    """
    Conector para integração com Haystack.
    Encapsula a execução de pipelines de processamento de linguagem natural e RAG.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.pipeline: Any = None

    def initialize(self) -> None:
        """
        Inicializa o conector recebendo a instância do pipeline via config.
        """
        self.pipeline = self.config.get("pipeline")
        if not self.pipeline:
            raise IntegrationError("Nenhum pipeline Haystack válido foi fornecido na configuração.")
        
        self._is_initialized = True
        logger.info("HaystackIntegration inicializada com sucesso.")

    def health_check(self) -> bool:
        """Verifica se o pipeline está instanciado e operacional."""
        self._validate_initialization()
        return self.pipeline is not None

    def execute(self, data: Dict[str, Any], **kwargs: Any) -> Any:
        """
        Executa o pipeline do Haystack com os dados de entrada fornecidos.
        
        Args:
            data (Dict[str, Any]): Dicionário contendo os dados/parâmetros de entrada para o pipeline.
            **kwargs: Parâmetros adicionais para o método run.
            
        Returns:
            Any: Resultado estruturado retornado pelo pipeline do Haystack.
        """
        self._validate_initialization()
        try:
            logger.info("Executando pipeline Haystack...")
            result = self.pipeline.run(data, **kwargs)
            return result
        except Exception as e:
            logger.error("Erro durante a execução do pipeline Haystack: %s", str(e))
            raise IntegrationError(f"Falha na execução do Haystack: {e}") from e
