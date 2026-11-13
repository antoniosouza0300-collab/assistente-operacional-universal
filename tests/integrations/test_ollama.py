"""
Testes Unitários para a Integração Ollama - Assistente Operacional Universal
Valida inicialização, health check, execução bem-sucedida, política de retry e tratamento de falhas.
"""

import pytest
from unittest.mock import patch, MagicMock
from integrations.base import IntegrationError
from integrations.ollama.client import OllamaIntegration


@pytest.fixture
def ollama_config():
    return {
        "base_url": "http://localhost:11434",
        "default_model": "llama3",
        "timeout": 10,
        "max_retries": 3,
        "backoff_factor": 0.1  # Reduzido para agilizar os testes
    }


def test_initialization_success(ollama_config):
    """Verifica se o conector inicializa corretamente com as configurações fornecidas."""
    client = OllamaIntegration(ollama_config)
    client.initialize()
    
    assert client.is_initialized is True
    assert client.base_url == "http://localhost:11434"
    assert client.default_model == "llama3"
    assert client.max_retries == 3


def test_execute_uninitialized(ollama_config):
    """Garante que executar sem inicializar lança IntegrationError."""
    client = OllamaIntegration(ollama_config)
    with pytest.raises(IntegrationError, match="não foi inicializado"):
        client.execute(prompt="Teste")


@patch("integrations.ollama.client.requests.get")
def test_health_check_success(mock_get, ollama_config):
    """Testa o health_check retornando sucesso (status 200)."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    client = OllamaIntegration(ollama_config)
    client.initialize()
    
    assert client.health_check() is True
    mock_get.assert_called_once_with("http://localhost:11434/api/tags", timeout=5)


@patch("integrations.ollama.client.requests.get")
def test_health_check_failure(mock_get, ollama_config):
    """Testa o health_check quando o servidor falha ou retorna erro."""
    mock_get.side_effect = Exception("Conexão recusada")

    client = OllamaIntegration(ollama_config)
    client.initialize()
    
    assert client.health_check() is False


@patch("integrations.ollama.client.requests.post")
def test_execute_success(mock_post, ollama_config):
    """Valida a execução de inferência bem-sucedida."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": "Olá, mundo!",
        "total_duration": 123456,
        "eval_count": 10
    }
    mock_post.return_value = mock_response

    client = OllamaIntegration(ollama_config)
    client.initialize()
    
    result = client.execute(prompt="Diga olá")
    
    assert result["response"] == "Olá, mundo!"
    assert result["model"] == "llama3"
    assert result["eval_count"] == 10
    mock_post.assert_called_once()


@patch("integrations.ollama.client.time.sleep", return_value=None)  # Ignora o delay real nos testes
@patch("integrations.ollama.client.requests.post")
def test_execute_retry_success_on_second_try(mock_post, mock_sleep, ollama_config):
    """Testa o mecanismo de retry: falha na 1ª tentativa e sucesso na 2ª."""
    fail_response = MagicMock()
    fail_response.status_code = 500
    fail_response.text = "Internal Server Error"

    success_response = MagicMock()
    success_response.status_code = 200
    success_response.json.return_value = {
        "response": "Sucesso após retry",
        "total_duration": 100,
        "eval_count": 5
    }

    mock_post.side_effect = [fail_response, success_response]

    client = OllamaIntegration(ollama_config)
    client.initialize()
    
    result = client.execute(prompt="Teste de retry")
    
    assert result["response"] == "Sucesso após retry"
    assert mock_post.call_count == 2


@patch("integrations.ollama.client.time.sleep", return_value=None)
@patch("integrations.ollama.client.requests.post")
def test_execute_max_retries_exceeded(mock_post, mock_sleep, ollama_config):
    """Garante que IntegrationError é lançado após esgotar todas as tentativas."""
    mock_post.side_effect = Exception("Erro de rede persistente")

    client = OllamaIntegration(ollama_config)
    client.initialize()
    
    with pytest.raises(IntegrationError, match="Não foi possível obter resposta do Ollama"):
        client.execute(prompt="Teste falha total")
    
    assert mock_post.call_count == ollama_config["max_retries"]
    
def test_execute_max_retries_exceeded(ollama_client):
    """Garante que o cliente lança exceção após esgotar o número máximo de tentativas."""
    # Configura o mock para falhar persistentemente
    # ...
    with pytest.raises(Exception, match="Erro de rede persistente"):
        ollama_client.execute(prompt="Teste de falha")
