"""
Testes Unitários para a Integração DSPy - Assistente Operacional Universal
Valida inicialização, health check, execução de programas e tratamento de falhas.
"""

import pytest
from unittest.mock import MagicMock
from integrations.base import IntegrationError
from integrations.dspy.client import DSPyIntegration


@pytest.fixture
def mock_program():
    """Cria um mock para simular um programa ou módulo DSPy."""
    program = MagicMock()
    program.return_value = {"answer": "Resultado gerado pelo DSPy"}
    return program


@pytest.fixture
def dspy_config(mock_program):
    return {
        "program": mock_program
    }


def test_initialization_success(dspy_config, mock_program):
    """Verifica se o conector DSPy inicializa corretamente."""
    client = DSPyIntegration(dspy_config)
    client.initialize()
    
    assert client.is_initialized is True
    assert client.program == mock_program


def test_initialization_missing_program():
    """Garante que inicializar sem um programa configurado lança IntegrationError."""
    client = DSPyIntegration({})
    with pytest.raises(IntegrationError, match="Nenhum programa ou módulo DSPy válido"):
        client.initialize()


def test_execute_uninitialized(dspy_config):
    """Garante que executar sem chamar initialize() lança IntegrationError."""
    client = DSPyIntegration(dspy_config)
    with pytest.raises(IntegrationError, match="não foi inicializado"):
        client.execute(question="O que é DSPy?")


def test_health_check_success(dspy_config):
    """Valida o health check quando o programa está presente e inicializado."""
    client = DSPyIntegration(dspy_config)
    client.initialize()
    
    assert client.health_check() is True


def test_execute_success(dspy_config, mock_program):
    """Valida a execução bem-sucedida do programa no DSPy."""
    client = DSPyIntegration(dspy_config)
    client.initialize()
    
    result = client.execute(question="Como funciona o DSPy?")
    
    assert result["answer"] == "Resultado gerado pelo DSPy"
    mock_program.assert_called_once_with(question="Como funciona o DSPy?")


def test_execute_program_failure(dspy_config, mock_program):
    """Garante que falhas internas no programa são tratadas e convertidas em IntegrationError."""
    mock_program.side_effect = Exception("Erro interno na otimização DSPy")

    client = DSPyIntegration(dspy_config)
    client.initialize()
    
    with pytest.raises(IntegrationError, match="Falha na execução do DSPy"):
        client.execute(question="teste falha")
