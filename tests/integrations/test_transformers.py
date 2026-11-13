"""
Testes Unitários para a Integração Transformers - Assistente Operacional Universal
Valida inicialização, health check, execução de pipelines e tratamento de falhas.
"""

import pytest
from unittest.mock import MagicMock
from integrations.base import IntegrationError
from integrations.transformers.client import TransformersIntegration


@pytest.fixture
def mock_pipeline():
    """Cria um mock para simular um pipeline Hugging Face."""
    pipeline = MagicMock()
    pipeline.return_value = [{"generated_text": "Texto gerado pelo Hugging Face Transformers"}]
    return pipeline


@pytest.fixture
def transformers_config(mock_pipeline):
    return {
        "pipeline": mock_pipeline
    }


def test_initialization_success(transformers_config, mock_pipeline):
    """Verifica se o conector Transformers inicializa corretamente."""
    client = TransformersIntegration(transformers_config)
    client.initialize()
    
    assert client.is_initialized is True
    assert client.pipeline == mock_pipeline


def test_initialization_missing_pipeline():
    """Garante que inicializar sem um pipeline configurado lança IntegrationError."""
    client = TransformersIntegration({})
    with pytest.raises(IntegrationError, match="Nenhum pipeline Transformers válido"):
        client.initialize()


def test_execute_uninitialized(transformers_config):
    """Garante que executar sem chamar initialize() lança IntegrationError."""
    client = TransformersIntegration(transformers_config)
    with pytest.raises(IntegrationError, match="não foi inicializado"):
        client.execute(inputs="Teste Transformers")


def test_health_check_success(transformers_config):
    """Valida o health check quando o pipeline está presente e inicializado."""
    client = TransformersIntegration(transformers_config)
    client.initialize()
    
    assert client.health_check() is True


def test_execute_success(transformers_config, mock_pipeline):
    """Valida a execução bem-sucedida do pipeline Transformers."""
    client = TransformersIntegration(transformers_config)
    client.initialize()
    
    inputs = "O que é Hugging Face?"
    result = client.execute(inputs=inputs)
    
    assert result[0]["generated_text"] == "Texto gerado pelo Hugging Face Transformers"
    mock_pipeline.assert_called_once_with(inputs)


def test_execute_pipeline_failure(transformers_config, mock_pipeline):
    """Garante que falhas internas no pipeline são tratadas e convertidas em IntegrationError."""
    mock_pipeline.side_effect = Exception("Erro de inferência no modelo")

    client = TransformersIntegration(transformers_config)
    client.initialize()
    
    with pytest.raises(IntegrationError, match="Falha na execução do Transformers"):
        client.execute(inputs="teste falha")
