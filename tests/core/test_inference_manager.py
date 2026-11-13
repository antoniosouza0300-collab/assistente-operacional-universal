"""
Testes Unitários para o InferenceManager - Assistente Operacional Universal
Valida o registro, inicialização tardia, tratamento de erros e execução de inferências.
"""

import pytest
from unittest.mock import MagicMock
from core.inference.manager import InferenceManager
from integrations.base import IntegrationError


@pytest.fixture
def mock_integration():
    """Cria um mock para simular um conector válido."""
    client = MagicMock()
    client.is_initialized = True
    client.execute.return_value = {"response": "Resultado gerado pelo Core"}
    return client


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
    
    result = manager.execute("ollama", prompt="Teste Core")
    
    assert result["response"] == "Resultado gerado pelo Core"
    mock_integration.execute.assert_called_once_with(prompt="Teste Core")
