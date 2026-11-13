"""
Conector vLLM - Assistente Operacional Universal
Gerencia a inicialização e inferência de alta performance para modelos de linguagem com vLLM.
"""

import logging
from typing import Any, Dict, Optional

from integrations.base import BaseIntegration, IntegrationError

logger = logging.getLogger(__name__)


class VLLMIntegration(BaseIntegration):
    """
    Conector para integração com vLLM.
    Encapsula a inferência otimizada de alta performance e gerenciamento de engine.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.llm_engine: Any = None

    def initialize(self) -> None:
        """
        Inicializa o conector recebendo a instância do engine vLLM via config.
        """
        self.llm_engine = self.config.get("llm_engine")
        if not self.llm_engine:
            raise IntegrationError("Nenhuma instância de vLLM LLM engine válida foi fornecida na configuração.")
        
        self._is_initialized = True
        logger.info("VLLMIntegration inicializada com sucesso.")

    def health_check(self) -> bool:
        """Verifica se o engine vLLM está instanciado e operacional."""
        self._validate_initialization()
        return self.llm_engine is not None

    def execute(self, prompts: Any, sampling_params: Optional[Any] = None, **kwargs: Any) -> Any:
        """
        Executa a geração de texto utilizando o engine vLLM.
        
        Args:
            prompts (Any): String ou lista de strings de prompts de entrada.
            sampling_params (Optional[Any]): Parâmetros de amostragem (SamplingParams) do vLLM.
            **kwargs: Parâmetros adicionais para o método generate.
            
        Returns:
            Any: Lista de objetos de saída retornada pelo vLLM.
        """
        self._validate_initialization()
        try:
            logger.info("Executando inferência no vLLM...")
            if sampling_params is not None:
                result = self.llm_engine.generate(prompts, sampling_params, **kwargs)
            else:
                result = self.llm_engine.generate(prompts, **kwargs)
            return result
        except Exception as e:
            logger.error("Erro durante a execução do vLLM: %s", str(e))
            raise IntegrationError(f"Falha na execução do vLLM: {e}") from e
