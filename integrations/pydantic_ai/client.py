"""
Conector Pydantic AI - Assistente Operacional Universal
Gerencia a inicialização e execução de agentes estruturados baseados em Pydantic AI.
"""

import logging
from typing import Any, Dict, Optional

from integrations.base import BaseIntegration, IntegrationError

logger = logging.getLogger(__name__)


class PydanticAIIntegration(BaseIntegration):
    """
    Conector para integração com Pydantic AI.
    Encapsula a execução de agentes tipados com validação rigorosa de modelos Pydantic.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.agent: Any = None

    def initialize(self) -> None:
        """
        Inicializa o conector recebendo a instância do agente Pydantic AI via config.
        """
        self.agent = self.config.get("agent")
        if not self.agent:
            raise IntegrationError("Nenhuma instância de Agente Pydantic AI válida foi fornecida na configuração.")
        
        self._is_initialized = True
        logger.info("PydanticAIIntegration inicializada com sucesso.")

    def health_check(self) -> bool:
        """Verifica se o agente está instanciado e operacional."""
        self._validate_initialization()
        return self.agent is not None

    def execute(self, prompt: str, **kwargs: Any) -> Any:
        """
        Executa a chamada síncrona no agente Pydantic AI.
        
        Args:
            prompt (str): Texto de entrada/pergunta para o agente.
            **kwargs: Parâmetros adicionais para o método run_sync.
            
        Returns:
            Any: Resposta estruturada retornada pelo agente Pydantic AI.
        """
        self._validate_initialization()
        try:
            logger.info("Executando agente Pydantic AI...")
            result = self.agent.run_sync(prompt, **kwargs)
            return result
        except Exception as e:
            logger.error("Erro durante a execução do agente Pydantic AI: %s", str(e))
            raise IntegrationError(f"Falha na execução do Pydantic AI: {e}") from e
