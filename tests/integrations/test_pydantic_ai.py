"""
Testes Unitários para a Integração Pydantic AI - Assistente Operacional Universal
Valida inicialização, health check, execução de agentes e tratamento de falhas.
"""

import pytest
from unittest.mock import MagicMock
from integrations.base import IntegrationError
from integrations.pydantic_ai.client import PydanticAIIntegration


@pytest.fixture
def mock_agent():
    """Cria um mock para simular um Agent do Pydantic AI."""
    agent = MagicMock()
    mock_result = MagicMock()
    mock_result.data = {"output": "Dados validados pelo Pydantic AI"}
    agent.run_sync.return_value = mock_result
    return agent


@pytest.fixture
def pydantic_ai_config(mock_agent):
    return {
        "agent": mock_agent
    }


def test_initialization_success(pydantic_ai_config, mock_agent):
    """Verifica se o conector Pydantic AI inicializa corretamente."""
    client = PydanticAIIntegration(pydantic_ai_config)
    client.initialize()
    
    assert client.is_initialized is True
    assert client.agent == mock_agent


def test_initialization_missing_agent():
    """Garante que inicializar sem um agente configurado lança IntegrationError."""
    client = PydanticAIIntegration({})
    with pytest.raises(IntegrationError, match="Nenhuma instância de Agente Pydantic AI válida"):
        client.initialize()


def test_execute_uninitialized(pydantic_ai_config):
    """Garante que executar sem chamar initialize() lança IntegrationError."""
    client = PydanticAIIntegration(pydantic_ai_config)
    with pytest.raises(IntegrationError, match="não foi inicializado"):
        client.execute(prompt="Teste")


def test_health_check_success(pydantic_ai_config):
    """Valida o health check quando o agente está presente e inicializado."""
    client = PydanticAIIntegration(pydantic_ai_config)
    client.initialize()
    
    assert client.health_check() is True


def test_execute_success(pydantic_ai_config, mock_agent):
    """Valida a execução bem-sucedida do agente no Pydantic AI."""
    client = PydanticAIIntegration(pydantic_ai_config)
    client.initialize()
    
    prompt = "Analise os dados estruturados"
    result = client.execute(prompt=prompt)
    
    assert result.data["output"] == "Dados validados pelo Pydantic AI"
    mock_agent.run_sync.assert_called_once_with(prompt)


def test_execute_agent_failure(pydantic_ai_config, mock_agent):
    """Garante que falhas internas no agente são tratadas e convertidas em IntegrationError."""
    mock_agent.run_sync.side_effect = Exception("Erro de validação no modelo Pydantic")

    client = PydanticAIIntegration(pydantic_ai_config)
    client.initialize()
    
    with pytest.raises(IntegrationError, match="Falha na execução do Pydantic AI"):
        client.execute(prompt="teste falha")
