"""
Contrato Base de Integrações - Assistente Operacional Universal
Define a Interface Abstrata (ABC) para todos os conectores (LangGraph, Ollama, CrewAI, etc.).
"""

from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class IntegrationError(Exception):
    """Exceção base para erros ocorridos em módulos de integração."""
    pass


class BaseIntegration(ABC):
    """
    Classe Abstrata Base para padronização de conectores externos e frameworks de IA.
    Enforça o ciclo de vida: initialize -> health_check -> execute.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config: Dict[str, Any] = config or {}
        self._is_initialized: bool = False
        logger.debug("Instanciando conector base: %s", self.__class__.__name__)

    @abstractmethod
    def initialize(self) -> None:
        """
        Inicializa clientes, carrega modelos, autentica ou estabelece conexões necessárias.
        Deve definir `self._is_initialized = True` ao concluir com sucesso.
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Verifica se a integração está operacional e responsiva.
        
        Returns:
            bool: True se o serviço/modelo estiver saudável, False caso contrário.
        """
        pass

    @abstractmethod
    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """
        Executa a tarefa principal associada ao conector (inferência, fluxo, processamento).
        
        Args:
            *args: Argumentos posicionais dinâmicos.
            **kwargs: Parâmetros nomeados para a execução.
            
        Returns:
            Any: Resultado estruturado da execução.
        """
        pass

    @property
    def is_initialized(self) -> bool:
        """Retorna o estado atual de inicialização do conector."""
        return self._is_initialized

    def _validate_initialization(self) -> None:
        """Garante que o conector foi inicializado antes de qualquer execução."""
        if not self._is_initialized:
            raise IntegrationError(
                f"O conector '{self.__class__.__name__}' não foi inicializado. Chame .initialize() primeiro."
            )
