"""
Testes Unitários para o WorkflowOrchestrator - Assistente Operacional Universal
Valida o encadeamento de etapas, propagação de contexto, transformação de saídas e tratamento de erros.
"""

import pytest
from unittest.mock import MagicMock
from core.inference.manager import InferenceManager
from core.orchestrator.engine import WorkflowOrchestrator
from integrations.base import IntegrationError


@pytest.fixture
def configured_manager():
    """Cria um InferenceManager com dois conectores simulados (ex: Ollama + Fabric)."""
    manager = InferenceManager()

    ollama_mock = MagicMock()
    ollama_mock.is_initialized = True
    ollama_mock.execute.return_value = {"response": "Rascunho técnico gerado pelo Ollama"}

    fabric_mock = MagicMock()
    fabric_mock.is_initialized = True
    fabric_mock.execute.return_value = "Resumo executivo refinado pelo Fabric"

    manager.register_integration("ollama", ollama_mock)
    manager.register_integration("fabric", fabric_mock)
    return manager


def test_workflow_empty_raises_error(configured_manager):
    """Garante que executar um workflow sem etapas lança IntegrationError."""
    orchestrator = WorkflowOrchestrator(configured_manager)
    with pytest.raises(IntegrationError, match="não possui etapas configuradas"):
        orchestrator.run({"topic": "Arquitetura de IA"})


def test_workflow_chained_execution_success(configured_manager):
    """Valida o encadeamento entre múltiplos conectores com propagação de estado."""
    orchestrator = WorkflowOrchestrator(configured_manager)

    orchestrator.add_step(
        name="gerar_rascunho",
        integration_name="ollama",
        input_mapper=lambda ctx: {"prompt": f"Escreva sobre {ctx['topic']}"},
        output_key="draft",
        transform_output=lambda res: res["response"],
    ).add_step(
        name="extrair_insights",
        integration_name="fabric",
        input_mapper=lambda ctx: {"text": ctx["draft"], "pattern_name": "extract_wisdom"},
        output_key="final_summary",
    )

    final_context = orchestrator.run({"topic": "Sistemas Multi-Agente"})

    assert final_context["topic"] == "Sistemas Multi-Agente"
    assert final_context["draft"] == "Rascunho técnico gerado pelo Ollama"
    assert final_context["final_summary"] == "Resumo executivo refinado pelo Fabric"


def test_workflow_step_failure_propagates_integration_error(configured_manager):
    """Garante que falhas no input_mapper ou na execução interrompem o fluxo com IntegrationError."""
    orchestrator = WorkflowOrchestrator(configured_manager)

    orchestrator.add_step(
        name="etapa_quebrada",
        integration_name="ollama",
        input_mapper=lambda ctx: {"prompt": ctx["chave_inexistente"]},  # Gera KeyError
        output_key="out",
    )

    with pytest.raises(IntegrationError, match="Falha na etapa 'etapa_quebrada'"):
        orchestrator.run({"topic": "Teste"})
