"""
Configurações do Sistema (Config) - Assistente Operacional Universal
Gerenciamento centralizado de variáveis de ambiente e parâmetros globais utilizando Pydantic BaseSettings.
"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Classe de configuração global do sistema.
    Carrega valores do ambiente do sistema operacional ou de um arquivo .env na raiz do projeto.
    """
    # Configurações Gerais
    environment: str = "development"
    log_level: str = "INFO"
    app_name: str = "Assistente Operacional Universal"

    # Conectores e Servidores Locais
    ollama_base_url: str = "http://localhost:11434"
    ollama_default_model: str = "llama3"
    vllm_base_url: str = "http://localhost:8000/v1"
    vllm_default_model: str = "meta-llama/Meta-Llama-3-8B-Instruct"

    # Chaves de API para Provedores em Nuvem (Opcionais por padrão)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    huggingface_hub_token: Optional[str] = None

    # Configuração do Pydantic Settings
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Instância global de configurações compartilhada em todo o projeto
settings = Settings()
