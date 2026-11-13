"""
Testes Unitários para a Integração vLLM - Assistente Operacional Universal
Valida inicialização, health check, execução de inferência e tratamento de falhas.
"""

import pytest
from unittest.mock import MagicMock
from integrations.base import IntegrationError
from integrations.vllm.client import VLLMIntegration


@pytest.fixture
def mock_vllm_engine():
    """Cria um mock para simular o engine LLM do vLLM."""
    engine = MagicMock()
    mock_output = MagicMock()
    mock_output.outputs = [MagicMock(text="Texto gerado pelo vLLM de alta performance")]
    engine.generate.return_value = [mock_output]
    return engine


@pytest.fixture
def vllm_config(mock_vllm_engine):
    return {
        "llm_engine": mock_vllm_engine
    }


def test_initialization_success(vllm_config, mock_vllm_engine):
    """Verifica se o conector vLLM inicializa corretamente."""
    client = VLLMIntegration(vllm_config)
    client.initialize()
    
    assert client.is_initialized is True
    assert client.llm_engine == mock_vllm_engine


def test_initialization_missing_engine():
    """Garante que inicializar sem um llm_engine configurado lança IntegrationError."""
    client = VLLMIntegration({})
    with pytest.raises(IntegrationError, match="Nenhuma instância de vLLM LLM engine válida"):
        client.initialize()


def test_execute_uninitialized(vllm_config):
    """Garante que executar sem chamar initialize() lança IntegrationError."""
    client = VLLMIntegration(vllm_config)
    with pytest.raises(IntegrationError, match="não foi inicializado"):
        client.execute(prompts="Teste vLLM")


def test_health_check_success(vllm_config):
    """Valida o health check quando o llm_engine está presente e inicializado."""
    client = VLLMIntegration(vllm_config)
    client.initialize()
    
    assert client.health_check() is True


def test_execute_success(vllm_config, mock_vllm_engine):
    """Valida a execução bem-sucedida de inferência no vLLM."""
    client = VLLMIntegration(vllm_config)
    client.initialize()
    
    prompts = "O que é vLLM?"
    result = client.execute(prompts=prompts)
    
    assert result[0].outputs[0].text == "Texto gerado pelo vLLM de alta performance"
    mock_vllm_engine.generate.assert_called_once_with(prompts)


def test_execute_success_with_sampling_params(vllm_config, mock_vllm_engine):
    """Valida a execução com sampling_params customizados."""
    client = VLLMIntegration(vllm_config)
    client.initialize()
    
    prompts = ["Prompt 1", "Prompt 2"]
    mock_sampling_params = MagicMock()
    result = client.execute(prompts=prompts, sampling_params=mock_sampling_params)
    
    assert len(result) == 1
    mock_vllm_engine.generate.assert_called_once_with(prompts, mock_sampling_params)


def test_execute_engine_failure(vllm_config, mock_vllm_engine):
    """Garante que falhas internas no vLLM são tratadas e convertidas em IntegrationError."""
    mock_vllm_engine.generate.side_effect = Exception("Erro de alocação de memória na GPU")

    client = VLLMIntegration(vllm_config)
    client.initialize()
    
    with pytest.raises(IntegrationError, match="Falha na execução do vLLM"):
        client.execute(prompts="teste falha")
