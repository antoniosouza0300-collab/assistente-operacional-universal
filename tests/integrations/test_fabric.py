"""
Testes Unitários para a Integração Fabric - Assistente Operacional Universal
Valida inicialização, health check, execução de padrões e tratamento de falhas.
"""

import pytest
from unittest.mock import MagicMock
from integrations.base import IntegrationError
from integrations.fabric.client import FabricIntegration


@pytest.fixture
def mock_pattern_runner():
    """Cria um mock para simular o executor de padrões do Fabric."""
    runner = MagicMock()
    runner.return_value = "Insights extraídos com sucesso pelo padrão Fabric"
    return runner


@pytest.fixture
def fabric_config(mock_pattern_runner):
    return {
        "pattern_runner": mock_pattern_runner
    }


def test_initialization_success(fabric_config, mock_pattern_runner):
    """Verifica se o conector Fabric inicializa corretamente."""
    client = FabricIntegration(fabric_config)
    client.initialize()
    
    assert client.is_initialized is True
    assert client.pattern_runner == mock_pattern_runner


def test_initialization_missing_runner():
    """Garante que inicializar sem um pattern_runner configurado lança IntegrationError."""
    client = FabricIntegration({})
    with pytest.raises(IntegrationError, match="Nenhum pattern_runner Fabric válido"):
        client.initialize()


def test_execute_uninitialized(fabric_config):
    """Garante que executar sem chamar initialize() lança IntegrationError."""
    client = FabricIntegration(fabric_config)
    with pytest.raises(IntegrationError, match="não foi inicializado"):
        client.execute(text="Texto de teste", pattern_name="summarize")


def test_health_check_success(fabric_config):
    """Valida o health check quando o pattern_runner está presente e inicializado."""
    client = FabricIntegration(fabric_config)
    client.initialize()
    
    assert client.health_check() is True


def test_execute_success(fabric_config, mock_pattern_runner):
    """Valida a execução bem-sucedida de um padrão no Fabric."""
    client = FabricIntegration(fabric_config)
    client.initialize()
    
    text = "Artigo técnico sobre engenharia de IA"
    pattern = "extract_wisdom"
    result = client.execute(text=text, pattern_name=pattern)
    
    assert result == "Insights extraídos com sucesso pelo padrão Fabric"
    mock_pattern_runner.assert_called_once_with(text, pattern_name=pattern)


def test_execute_runner_failure(fabric_config, mock_pattern_runner):
    """Garante que falhas internas no executor são tratadas e convertidas em IntegrationError."""
    mock_pattern_runner.side_effect = Exception("Erro ao carregar o arquivo de padrão Fabric")

    client = FabricIntegration(fabric_config)
    client.initialize()
    
    with pytest.raises(IntegrationError, match="Falha na execução do Fabric"):
        client.execute(text="teste falha", pattern_name="summarize")
