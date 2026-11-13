
"""
Conector Ollama - Assistente Operacional Universal.
Integração resiliente com modelos locais, retry e logs estruturados.
"""

import time
from typing import Any, Dict, Optional

import requests

from core.logging import get_logger
from integrations.base import BaseIntegration, IntegrationError

logger = get_logger(__name__)


class OllamaIntegration(BaseIntegration):
    """Conector para inferência em modelos locais via API Ollama."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)

        self.base_url = self.config.get(
            "base_url", "http://localhost:11434"
        ).rstrip("/")
        self.default_model = self.config.get("default_model", "llama3")
        self.timeout = int(self.config.get("timeout", 60))
        self.max_retries = int(self.config.get("max_retries", 3))
        self.backoff_factor = float(
            self.config.get("backoff_factor", 1.5)
        )

    def initialize(self) -> None:
        """Inicializa o conector Ollama."""
        if self.max_retries < 1:
            raise IntegrationError("max_retries deve ser maior que zero.")

        if self.timeout <= 0:
            raise IntegrationError("timeout deve ser maior que zero.")

        self._is_initialized = True

        logger.info(
            "Conector Ollama inicializado",
            base_url=self.base_url,
            model=self.default_model,
        )

    def health_check(self) -> bool:
        """Verifica a disponibilidade do servidor Ollama."""
        self._validate_initialization()

        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )
            return response.status_code == 200

        except Exception as exc:
            logger.warning(
                "Health check do Ollama falhou",
                error=str(exc),
            )
            return False

    def execute(
        self,
        prompt: str,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Executa inferência com retry e backoff progressivo."""
        self._validate_initialization()

        if not prompt:
            raise IntegrationError(
                "O parâmetro 'prompt' é obrigatório para execução no Ollama."
            )

        target_model = model or self.default_model
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": target_model,
            "prompt": prompt,
            "stream": False,
            **kwargs,
        }

        last_exception: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(
                    "Enviando requisição para Ollama",
                    attempt=attempt,
                    max_retries=self.max_retries,
                    model=target_model,
                )

                response = requests.post(
                    url,
                    json=payload,
                    timeout=self.timeout,
                )

                if response.status_code != 200:
                    raise RuntimeError(
                        f"Erro HTTP {response.status_code}: "
                        f"{response.text}"
                    )

                data = response.json()

                return {
                    "model": target_model,
                    "response": data.get("response", ""),
                    "total_duration": data.get("total_duration", 0),
                    "eval_count": data.get("eval_count", 0),
                }

            except Exception as exc:
                last_exception = exc

                logger.warning(
                    "Falha na tentativa de inferência no Ollama",
                    attempt=attempt,
                    error=str(exc),
                )

                if attempt < self.max_retries:
                    delay = self.backoff_factor ** attempt

                    logger.info(
                        "Aguardando antes de nova tentativa",
                        delay=delay,
                    )

                    time.sleep(delay)

        logger.error(
            "Número máximo de tentativas excedido no Ollama",
            error=str(last_exception),
        )

        raise IntegrationError(
            "Não foi possível obter resposta do Ollama"
        ) from last_exception
