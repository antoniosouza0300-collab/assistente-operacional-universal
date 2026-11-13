"""
Gerenciador de Inferência (Core) - Assistente Operacional Universal
Orquestra, valida e padroniza as chamadas aos diferentes conectores de IA do framework.
"""

import logging
from typing import Any, Dict, Optional

from integrations.base import IntegrationError

logger = logging.getLogger(__name__)


class InferenceManager:
    """
    Gerenciador central de inferências e modelos.
    Mantém o registro dos conectores ativos e roteia as execuções de forma unificada.
    """

    def __init__(self) -> None:
        self.integrations: Dict[str, Any] = {}

    def register_integration(self, name: str, integration_client: Any) -> None:
        """
        Registra e inicializa um conector de integração no gerenciador.
        
        Args:
            name (str): Identificador único do conector (ex: 'ollama', 'vllm').
            integration_client (Any): Instância do conector herdado de BaseIntegration.
        """
        if not integration_client.is_initialized:
            try:
                integration_client.initialize()
            except Exception as e:
                logger.error("Falha ao inicializar a integração '%s': %s", name, str(e))
                raise IntegrationError(f"Não foi possível registrar a integração {name}: {e}") from e
        
        self.integrations[name] = integration_client
        logger.info("Integração '%s' registrada com sucesso no InferenceManager.", name)

    def get_integration(self, name: str) -> Any:
        """
        Retorna o conector registrado pelo nome.
        
        Args:
            name (str): Identificador do conector.
        """
        if name not in self.integrations:
            raise IntegrationError(f"A integração '{name}' não está registrada no InferenceManager.")
        return self.integrations[name]

    def execute(self, integration_name: str, **kwargs: Any) -> Any:
        """
        Executa a inferência ou operação utilizando o conector especificado.
        
        Args:
            integration_name (str): Nome do conector que realizará a execução.
            **kwargs: Argumentos passados diretamente para o método execute do conector.
            
        Returns:
            Any: Resultado retornado pela integração.
        """
        client = self.get_integration(integration_name)
        logger.info("Executando inferência via conector: '%s'", integration_name)
        return client.execute(**kwargs)
