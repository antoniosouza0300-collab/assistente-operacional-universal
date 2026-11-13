"""
Testes Unitários para a CLI - Assistente Operacional Universal
Valida o parsing de argumentos do argparse, execução bem-sucedida do workflow via CLI
e o tratamento adequado de falhas críticas (sys.exit).
"""

import sys
import pytest

from cli import main, create_parser
from core.orchestrator.engine import WorkflowOrchestrator
from integrations.base import IntegrationError


def test_parser_default_arguments():
    """Valida se o argparse configura os valores padrão corretamente quando nenhum argumento é passado."""
    parser = create_parser()
    args = parser.parse_args([])
    
    assert args.topic == "Sistemas Multi-Agente e Arquiteturas Modulares"
    assert args.env == "development"


def test_parser_custom_arguments():
    """Valida se o argparse captura argumentos personalizados (--topic e --env) corretamente."""
    parser = create_parser()
    args = parser.parse_args(["--topic", "Orquestração com LangGraph", "--env", "production"])
    
    assert args.topic == "Orquestração com LangGraph"
    assert args.env == "production"


def test_cli_execution_success(monkeypatch, capsys):
    """Valida a execução bem-sucedida do fluxo principal da CLI simulando os argumentos de entrada."""
    # Simula a passagem de parâmetros via linha de comando
    monkeypatch.setattr(sys, "argv", ["cli.py", "--topic", "Teste Automatizado CLI"])
    
    # Executa a função principal da CLI
    main()
    
    # Captura e valida a saída impressa no console
    captured = capsys.readouterr()
    assert "RESULTADO DA EXECUÇÃO VIA CLI" in captured.out
    assert "Teste Automatizado CLI" in captured.out


def test_cli_execution_failure_handles_error(monkeypatch):
    """Garante que falhas críticas no orquestrador interceptam a exceção e encerram a CLI com sys.exit(1)."""
    monkeypatch.setattr(sys, "argv", ["cli.py"])
    
    # Simula uma falha levantando IntegrationError durante a execução do workflow
    def mock_run_failure(self, initial_context):
        raise IntegrationError("Falha simulada na execução do workflow")

    monkeypatch.setattr(WorkflowOrchestrator, "run", mock_run_failure)

    # Verifica se o script encerra corretamente com código de saída 1
    with pytest.raises(SystemExit) as exc_info:
        main()
    
    assert exc_info.value.code == 1
