"""
Conector Ollama - Assistente Operacional Universal
Implementação resiliente para inferência local com suporte a retry e logs estruturados.
"""

import logging
import time
from typing import Any, Dict, Optional
requests_ok = True
try:
    import requests
except ImportError:
    requests_ok = False

from integrations.base import BaseIntegration, IntegrationError

logger = logging.getLogger(__name__)


class OllamaIntegration(BaseIntegration):
    """
    Conector para integração com servidores locais Ollama.
    Fornece inferência de texto com tratamento de falhas e reentransão (retry).
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(config)
        self.base_url: str = ""
        self.default_model: str = ""
        self.timeout: int = 60
        self.max_retries: int = 3
        self.backoff_factor: float = 1.5

    def initialize(self) -> None:
        """Inicializa as configurações do cliente Ollama a partir do dicionário de config."""
        if not requests_ok:
            raise IntegrationError("A biblioteca 'requests' é obrigatória para o conector Ollama. Instale via pip install requests.")
        
        self.base_url = self.config.get("base_url", "http://localhost:11434").rstrip("/")
        self.default_model = self.config.get("default_model", "llama3")
        self.timeout = int(self.config.get("timeout", 60))
        self.max_retries = int(self.config.get("max_retries", 3))
        
        self._is_initialized = True
        logger.info("OllamaIntegration inicializada. Endpoint: %s | Modelo Padrão: %s", self.base_url, self.default_model)

    def health_check(self) -> bool:
        """Verifica a disponibilidade do servidor Ollama consultando a API de tags."""
        self._validate_initialization()
        url = f"{self.base_url}/api/tags"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.debug("Health check do Ollama bem-sucedido.")
                return True
            logger.warning("Ollama retornou status code inesperado no health check: %d", response.status_code)
            return False
        except Exception as e:
            logger.error("Falha de conexão no health check do Ollama: %s", str(e))
            return False

    def execute(self, prompt: str, model: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """
        Executa a geração de texto no Ollama com política de retry e exponential backoff.
        
        Args:
            prompt (str): Texto de entrada/pergunta para o modelo.
            model (str, optional): Modelo a ser utilizado (sobrescreve o padrão).
            **kwargs: Parâmetros adicionais para a API do Ollama (temperature, options, etc.).
            
        Returns:
            Dict[str, Any]: Resposta estruturada contendo o texto gerado e metadados.
        """
        self._validate_initialization()
        target_model = model or self.default_model
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": target_model,
            "prompt": prompt,
            "stream": False,
            **kwargs
        }

        retries = 0
        while retries < self.max_retries:
            try:
                logger.info("Enviando requisição para Ollama (Tentativa %d/%d). Modelo: %s", retries + 1, self.max_retries, target_model)
                response = requests.post(url, json=payload, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "model": target_model,
                        "response": data.get("response", ""),
                        "total_duration": data.get("total_duration", 0),
                        "eval_count": data.get("eval_count", 0)
                    }
                
                logger.warning("Ollama retornou erro HTTP %d: %s", response.status_code, response.text)
                
            except requests.exceptions.RequestException as req_err:
                logger.warning("Erro de rede ao comunicar com Ollama (Tentativa %d): %s", retries + 1, str(req_err))
            
            retries += 1
            if retries < self.max_retries:
                sleep_time = self.backoff_factor ** retries
                logger.info("Aguardando %.2f segundos antes do próximo retry...", sleep_time)
                time.sleep(sleep_time)

        raise IntegrationError(f"Falha crítica: Não foi possível obter resposta do Ollama após {self.max_retries} tentativas.")
