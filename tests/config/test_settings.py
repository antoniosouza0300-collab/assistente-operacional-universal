"""
Testes Unitários para as Configurações - Assistente Operacional Universal
Valida valores padrão, sobrescrita por variáveis de ambiente e integridade do Pydantic.
"""

import os
import pytest
from config.settings import Settings


def test_settings_default_values():
    """Valida se os valores padrão das configurações são carregados corretamente sem .env."""
    env_backup = os.environ.copy()
    try:
        os.environ.pop("OPENAI_API_KEY", None)
        # Desativa o carregamento do .env físico para testar defaults puros
        custom_settings = Settings(_env_file=None)
        
        assert custom_settings.environment == "development"
        assert custom_settings.log_level == "INFO"
        assert custom_settings.ollama_base_url == "http://localhost:11434"
        assert custom_settings.openai_api_key is None
    finally:
        os.environ.clear()
        os.environ.update(env_backup)


def test_settings_override_via_env(monkeypatch):
    """Valida se as configurações respeitam e capturam as variáveis de ambiente."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-proj-mock-key-12345")

    custom_settings = Settings(_env_file=None)
    
    assert custom_settings.environment == "production"
    assert custom_settings.log_level == "DEBUG"
    assert custom_settings.openai_api_key == "sk-proj-mock-key-12345"
