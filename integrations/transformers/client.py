"""
Conector Transformers - Assistente Operacional Universal
Gerencia a inicialização e execução de pipelines de Hugging Face Transformers.
"""

import logging
from typing import Any, Dict, Optional

from integrations.base import BaseIntegration, IntegrationError

logger = logging.getLogger(__name__)


class TransformersIntegration(BaseIntegration):
    """
    Conector para integração com Hugging Face Transformers.
    Encapsula a execução de pipelines de processamento de linguagem natural e visão.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.pipeline: Any = None

    def initialize(self) -> None:
        """
        Inicializa o conector recebendo a instância do pipeline Transformers via config.
        """
        self.pipeline = self.config.get("pipeline")
        if not self.pipeline:
            raise IntegrationError("Nenhum pipeline Transformers válido foi fornecido na configuração.")
        
        self._is_initialized = True
        logger.info("TransformersIntegration inicializada com sucesso.")

    def health_check(self) -> bool:
        """Verifica se o pipeline está instanciado e operacional."""
        self._validate_initialization()
        return self.pipeline is not None

    def execute(self, inputs: Any, **kwargs: Any) -> Any:
        """
        Executa a inferência utilizando o pipeline do Transformers.
        
        Args:
            inputs (Any): Texto ou dados de entrada para o pipeline.
            **kwargs: Parâmetros adicionais para a chamada do pipeline.
            
        Returns:
            Any: Resultado estruturado gerado pelo modelo.
        """
        self._validate_initialization()
        try:
            logger.info("Executando pipeline Transformers...")
            result = self.pipeline(inputs, **kwargs)
            return result
        except Exception as e:
            logger.error("Erro durante a execução do Transformers: %s", str(e))
            raise IntegrationError(f"Falha na execução do Transformers: {e}") from e
