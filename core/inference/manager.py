"""
Gerenciador de Inferência (Core) - Assistente Operacional Universal
Orquestra, valida e padroniza as chamadas aos diferentes conectores de IA,
utilizando logging estruturado (structlog).
"""

from typing import Any, Dict, Optional

from config.settings import Settings, settings as default_settings
from core.logging import get_logger
from integrations.base import IntegrationError

logger = get_logger(__name__)


class InferenceManager:
    """
    Gerenciador central de inferências e modelos integrado com structlog e settings.
    """

    def __init__(self, settings_instance: Optional[Settings] = None) -> None:
        self.settings = settings_instance or default_settings
        self.integrations: Dict[str, Any] = {}
        logger.info("InferenceManager inicializado", environment=self.settings.environment)

    def register_integration(self, name: str, integration_client: Any) -> None:
        """Registra e inicializa um conector de integração."""
        if not integration_client.is_initialized:
            try:
                integration_client.initialize()
            except Exception as e:
                logger.error("Falha ao inicializar integração", integration=name, error=str(e))
                raise IntegrationError(f"Não foi possível registrar a integração {name}: {e}") from e
        
        self.integrations[name] = integration_client
        logger.info("Integração registrada com sucesso", integration=name)

    def get_integration(self, name: str) -> Any:
        """Retorna o conector registrado pelo nome."""
        if name not in self.integrations:
            logger.warning("Tentativa de acesso a integração não registrada", integration=name)
            raise IntegrationError(f"A integração '{name}' não está registrada no InferenceManager.")
        return self.integrations[name]

    def execute(self, integration_name: str, **kwargs: Any) -> Any:
        """Executa a inferência utilizando o conector especificado."""
        client = self.get_integration(integration_name)
        logger.info("Executando inferência", integration=integration_name)
        return client.execute(**kwargs)
