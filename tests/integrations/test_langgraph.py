"""
Testes Unitários para a Integração LangGraph - Assistente Operacional Universal
Valida inicialização, health check, execução bem-sucedida e tratamento de exceções no grafo.
"""

import pytest
from unittest.mock import MagicMock
from integrations.base import IntegrationError
from integrations.langgraph.client import LangGraphIntegration


@pytest.fixture
def mock_compiled_graph():
    """Cria um mock para simular um grafo compilado do LangGraph."""
    graph = MagicMock()
    graph.invoke.return_value = {"messages": ["Olá", "Resposta do Agente"], "status": "completed"}
    return graph


@pytest.fixture
def langgraph_config(mock_compiled_graph):
    return {
        "graph": mock_compiled_graph
    }


def test_initialization_success(langgraph_config, mock_compiled_graph):
    """Verifica se o conector LangGraph inicializa corretamente."""
    client = LangGraphIntegration(langgraph_config)
    client.initialize()
    
    assert client.is_initialized is True
    assert client.graph == mock_compiled_graph


def test_initialization_missing_graph():
    """Garante que inicializar sem um grafo configurado lança IntegrationError."""
    client = LangGraphIntegration({})
    with pytest.raises(IntegrationError, match="Nenhum grafo LangGraph válido foi fornecido"):
        client.initialize()


def test_execute_uninitialized(langgraph_config):
    """Garante que executar sem chamar initialize() lança IntegrationError."""
    client = LangGraphIntegration(langgraph_config)
    with pytest.raises(IntegrationError, match="não foi inicializado"):
        client.execute(state={"messages": []})


def test_health_check_success(langgraph_config):
    """Valida o health check quando o grafo está presente e inicializado."""
    client = LangGraphIntegration(langgraph_config)
    client.initialize()
    
    assert client.health_check() is True


def test_execute_success(langgraph_config, mock_compiled_graph):
    """Valida a execução bem-sucedida do grafo com o estado fornecido."""
    client = LangGraphIntegration(langgraph_config)
    client.initialize()
    
    initial_state = {"messages": ["Olá"]}
    result = client.execute(state=initial_state)
    
    assert result["status"] == "completed"
    assert len(result["messages"]) == 2
    mock_compiled_graph.invoke.assert_called_once_with(initial_state)


def test_execute_graph_failure(langgraph_config, mock_compiled_graph):
    """Garante que falhas internas no grafo são tratadas e convertidas em IntegrationError."""
    mock_compiled_graph.invoke.side_effect = Exception("Erro interno no nó do grafo")

    client = LangGraphIntegration(langgraph_config)
    client.initialize()
    
    with pytest.raises(IntegrationError, match="Falha na execução do grafo LangGraph"):
        client.execute(state={"messages": []})
