"""
Conector CrewAI - Assistente Operacional Universal
Gerencia a inicialização e execução de equipes de agentes autônomos (Crew).
"""

import logging
from typing import Any, Dict, Optional

from integrations.base import BaseIntegration, IntegrationError

logger = logging.getLogger(__name__)


class CrewAIIntegration(BaseIntegration):
    """
    Conector para orquestração de fluxos baseados em CrewAI.
    Encapsula a execução de Crews (equipes de agentes) e gerenciamento de estado.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.crew: Any = None

    def initialize(self) -> None:
        """
        Inicializa o conector recebendo a instância da Crew via config.
        """
        self.crew = self.config.get("crew")
        if not self.crew:
            raise IntegrationError("Nenhuma instância de Crew válida foi fornecida na configuração.")
        
        self._is_initialized = True
        logger.info("CrewAIIntegration inicializada com sucesso.")

    def health_check(self) -> bool:
        """Verifica se a Crew está instanciada e operacional."""
        self._validate_initialization()
        return self.crew is not None

    def execute(self, inputs: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Any:
        """
        Executa o kickoff da Crew com os inputs opcionais.
        
        Args:
            inputs (Optional[Dict[str, Any]]): Dicionário de variáveis de entrada para os agentes.
            **kwargs: Parâmetros adicionais para o método kickoff.
            
        Returns:
            Any: Resultado da execução da Crew.
        """
        self._validate_initialization()
        try:
            logger.info("Executando kickoff da CrewAI...")
            if inputs:
                result = self.crew.kickoff(inputs=inputs, **kwargs)
            else:
                result = self.crew.kickoff(**kwargs)
            return result
        except Exception as e:
            logger.error("Erro durante a execução da CrewAI: %s", str(e))
            raise IntegrationError(f"Falha na execução da CrewAI: {e}") from e
