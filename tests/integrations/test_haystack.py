"""
Testes Unitários para a Integração Haystack - Assistente Operacional Universal
Valida inicialização, health check, execução de pipelines e tratamento de falhas.
"""

import pytest
from unittest.mock import MagicMock
from integrations.base import IntegrationError
from integrations.haystack.client import HaystackIntegration


@pytest.fixture
def mock_pipeline():
    """Cria um mock para simular um Pipeline do Haystack."""
    pipeline = MagicMock()
    pipeline.run.return_value = {"reply": {"text": "Resposta gerada pelo Haystack"}}
    return pipeline


@pytest.fixture
def haystack_config(mock_pipeline):
    return {
        "pipeline": mock_pipeline
    }


def test_initialization_success(haystack_config, mock_pipeline):
    """Verifica se o conector Haystack inicializa corretamente."""
    client = HaystackIntegration(haystack_config)
    client.initialize()
    
    assert client.is_initialized is True
    assert client.pipeline == mock_pipeline


def test_initialization_missing_pipeline():
    """Garante que inicializar sem um pipeline configurado lança IntegrationError."""
    client = HaystackIntegration({})
    with pytest.raises(IntegrationError, match="Nenhum pipeline Haystack válido"):
        client.initialize()


def test_execute_uninitialized(haystack_config):
    """Garante que executar sem chamar initialize() lança IntegrationError."""
    client = HaystackIntegration(haystack_config)
    with pytest.raises(IntegrationError, match="não foi inicializado"):
        client.execute(data={"query": "teste"})


def test_health_check_success(haystack_config):
    """Valida o health check quando o pipeline está presente e inicializado."""
    client = HaystackIntegration(haystack_config)
    client.initialize()
    
    assert client.health_check() is True


def test_execute_success(haystack_config, mock_pipeline):
    """Valida a execução bem-sucedida do pipeline no Haystack."""
    client = HaystackIntegration(haystack_config)
    client.initialize()
    
    data = {"query": "O que é Haystack?"}
    result = client.execute(data=data)
    
    assert result["reply"]["text"] == "Resposta gerada pelo Haystack"
    mock_pipeline.run.assert_called_once_with(data)


def test_execute_pipeline_failure(haystack_config, mock_pipeline):
    """Garante que falhas internas no pipeline são tratadas e convertidas em IntegrationError."""
    mock_pipeline.run.side_effect = Exception("Erro interno no componente do pipeline")

    client = HaystackIntegration(haystack_config)
    client.initialize()
    
    with pytest.raises(IntegrationError, match="Falha na execução do Haystack"):
        client.execute(data={"query": "teste falha"})
