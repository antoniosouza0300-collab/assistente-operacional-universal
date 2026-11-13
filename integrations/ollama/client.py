"""
Conector Ollama - Assistente Operacional Universal
Implementa a integração com modelos locais executados via Ollama com suporte a retry.
"""

import time
import requests
from typing import Any, Dict, Optional

from core.logging import get_logger
from integrations.base import BaseIntegration, IntegrationError

logger = get_logger(__name__)


class OllamaIntegration(BaseIntegration):
    """Conector para modelos locais via API Ollama."""

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__()
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.default_model = config.get("default_model", "llama3")
        self.timeout = config.get("timeout", 30)
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 1)

    def initialize(self) -> None:
        """Inicializa e valida o conector Ollama."""
        self._is_initialized = True
        logger.info("Conector Ollama inicializado", base_url=self.base_url, model=self.default_model)

    def health_check(self) -> bool:
        """Verifica se o servidor Ollama está acessível."""
        self._validate_initialization()
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning("Health check do Ollama falhou", error=str(e))
            return False

    def execute(self, **kwargs: Any) -> Any:
        """Executa inferência no Ollama com política de retry."""
        self._validate_initialization()
        prompt = kwargs.get("prompt")
        model = kwargs.get("model", self.default_model)

        if not prompt:
            raise IntegrationError("O parâmetro 'prompt' é obrigatório para execução no Ollama.")

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }

        last_exception = None
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug("Enviando requisição para Ollama", attempt=attempt, model=model)
                response = requests.post(url, json=payload, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
            except Exception as e:
                last_exception = e
                logger.warning("Falha na tentativa de requisição ao Ollama", attempt=attempt, error=str(e))
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)

        logger.error("Número máximo de tentativas excedido no Ollama", error=str(last_exception))
        raise IntegrationError(f"Não foi possível obter resposta do Ollama após {self.max_retries} tentativas: {last_exception}")
