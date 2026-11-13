"""
Testes Unitários para a Integração CrewAI - Assistente Operacional Universal
Valida inicialização, health check, execução bem-sucedida e tratamento de falhas.
"""

import pytest
from unittest.mock import MagicMock
from integrations.base import IntegrationError
from integrations.crewai.client import CrewAIIntegration


@pytest.fixture
def mock_crew():
    """Cria um mock para simular uma Crew do CrewAI."""
    crew = MagicMock()
    crew.kickoff.return_value = "Resultado final da execução da Crew"
    return crew


@pytest.fixture
def crewai_config(mock_crew):
    return {
        "crew": mock_crew
    }


def test_initialization_success(crewai_config, mock_crew):
    """Verifica se o conector CrewAI inicializa corretamente."""
    client = CrewAIIntegration(crewai_config)
    client.initialize()
    
    assert client.is_initialized is True
    assert client.crew == mock_crew


def test_initialization_missing_crew():
    """Garante que inicializar sem uma Crew configurada lança IntegrationError."""
    client = CrewAIIntegration({})
    with pytest.raises(IntegrationError, match="Nenhuma instância de Crew válida foi fornecida"):
        client.initialize()


def test_execute_uninitialized(crewai_config):
    """Garante que executar sem chamar initialize() lança IntegrationError."""
    client = CrewAIIntegration(crewai_config)
    with pytest.raises(IntegrationError, match="não foi inicializado"):
        client.execute(inputs={"topic": "IA"})


def test_health_check_success(crewai_config):
    """Valida o health check quando a Crew está presente e inicializada."""
    client = CrewAIIntegration(crewai_config)
    client.initialize()
    
    assert client.health_check() is True


def test_execute_success_with_inputs(crewai_config, mock_crew):
    """Valida a execução bem-sucedida da Crew com inputs."""
    client = CrewAIIntegration(crewai_config)
    client.initialize()
    
    inputs = {"topic": "Engenharia de Software"}
    result = client.execute(inputs=inputs)
    
    assert result == "Resultado final da execução da Crew"
    mock_crew.kickoff.assert_called_once_with(inputs=inputs)


def test_execute_success_without_inputs(crewai_config, mock_crew):
    """Valida a execução bem-sucedida da Crew sem inputs."""
    client = CrewAIIntegration(crewai_config)
    client.initialize()
    
    result = client.execute()
    
    assert result == "Resultado final da execução da Crew"
    mock_crew.kickoff.assert_called_once_with()


def test_execute_crew_failure(crewai_config, mock_crew):
    """Garante que falhas internas na Crew são tratadas e convertidas em IntegrationError."""
    mock_crew.kickoff.side_effect = Exception("Erro interno nos agentes")

    client = CrewAIIntegration(crewai_config)
    client.initialize()
    
    with pytest.raises(IntegrationError, match="Falha na execução da CrewAI"):
        client.execute(inputs={})
