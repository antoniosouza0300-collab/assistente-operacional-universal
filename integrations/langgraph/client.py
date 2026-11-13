"""
Conector LangGraph - Assistente Operacional Universal
Gerencia a compilação e execução de fluxos stateful baseados em grafos.
"""

import logging
from typing import Any, Dict, Optional

from integrations.base import BaseIntegration, IntegrationError

logger = logging.getLogger(__name__)


class LangGraphIntegration(BaseIntegration):
    """
    Conector para orquestração de fluxos utilizando LangGraph.
    Encapsula a execução de grafos de estados e gerencia o ciclo de vida.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.graph: Any = None

    def initialize(self) -> None:
        """
        Inicializa o conector recebendo o grafo compilado ou os componentes de montagem via config.
        """
        self.graph = self.config.get("graph")
        if not self.graph:
            raise IntegrationError("Nenhum grafo LangGraph válido foi fornecido na configuração.")
        
        self._is_initialized = True
        logger.info("LangGraphIntegration inicializada com sucesso.")

    def health_check(self) -> bool:
        """Verifica se o grafo está instanciado e operacional."""
        self._validate_initialization()
        return self.graph is not None

    def execute(self, state: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """
        Executa o grafo LangGraph passando o estado inicial/atual.
        
        Args:
            state (Dict[str, Any]): Dicionário representando o estado inicial do grafo.
            **kwargs: Parâmetros adicionais para o método invoke (config, etc.).
            
        Returns:
            Dict[str, Any]: Estado final resultante da execução do grafo.
        """
        self._validate_initialization()
        try:
            logger.info("Executando fluxo LangGraph...")
            result = self.graph.invoke(state, **kwargs)
            return result
        except Exception as e:
            logger.error("Erro durante a execução do fluxo LangGraph: %s", str(e))
            raise IntegrationError(f"Falha na execução do grafo LangGraph: {e}") from e
