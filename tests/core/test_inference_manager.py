"""
Testes Unitários para o InferenceManager - Assistente Operacional Universal
Valida o registro, inicialização tardia, integração com settings e execução de inferências.
"""

import pytest
from unittest.mock import MagicMock
from config.settings import Settings
from core.inference.manager import InferenceManager
from integrations.base import IntegrationError


@pytest.fixture
def mock_integration():
    """Cria um mock para simular um conector válido."""
    client = MagicMock()
    client.is_initialized = True
    client.execute.return_value = {"response": "Resultado gerado pelo Core"}
    return client


def test_inference_manager_uses_default_settings():
    """Verifica se o InferenceManager carrega as configurações padrão quando nenhum settings é passado."""
    manager = InferenceManager()
    assert manager.settings is not None
    assert manager.settings.app_name == "Assistente Operacional Universal"


def test_inference_manager_accepts_custom_settings():
    """Valida a injeção de configurações customizadas no InferenceManager."""
    custom_settings = Settings(environment="testing", ollama_base_url="http://custom-ollama:11434")
    manager = InferenceManager(settings_instance=custom_settings)
    
    assert manager.settings.environment == "testing"
    assert manager.settings.ollama_base_url == "http://custom-ollama:11434"


def test_register_integration_success(mock_integration):
    """Verifica se o registro de uma integração já inicializada ocorre com sucesso."""
    manager = InferenceManager()
    manager.register_integration("ollama", mock_integration)
    
    assert "ollama" in manager.integrations
    assert manager.get_integration("ollama") == mock_integration


def test_register_uninitialized_integration():
    """Garante que integrações não inicializadas são inicializadas automaticamente no registro."""
    client = MagicMock()
    client.is_initialized = False
    
    manager = InferenceManager()
    manager.register_integration("vllm", client)
    
    client.initialize.assert_called_once()
    assert "vllm" in manager.integrations


def test_get_unregistered_integration():
    """Garante que solicitar um conector não registrado lança IntegrationError."""
    manager = InferenceManager()
    with pytest.raises(IntegrationError, match="não está registrada"):
        manager.get_integration("inexistente")


def test_execute_inference_success(mock_integration):
    """Valida a execução de inferência roteada corretamente pelo InferenceManager."""
    manager = InferenceManager()
    manager.register_integration("ollama", mock_integration)
    
    result = manager.execute("ollama", prompt="Teste Core com Settings")
    
    assert result["response"] == "Resultado gerado pelo Core"
    mock_integration.execute.assert_called_once_with(prompt="Teste Core com Settings")
