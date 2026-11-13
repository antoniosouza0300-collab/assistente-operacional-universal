"""
Ponto de Entrada Principal (Main) - Assistente Operacional Universal
Demonstra a inicialização do sistema, carregamento de configurações via Pydantic,
registro de conectores no InferenceManager e execução de um workflow orquestrado.
"""

import logging
from typing import Any

from config.settings import settings
from core.inference.manager import InferenceManager
from core.orchestrator.engine import WorkflowOrchestrator
from integrations.base import BaseIntegration

# Configuração de logging estruturado no console
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class DummyAIIntegration(BaseIntegration):
    """
    Conector de demonstração para fins educacionais e testes do main.py.
    Simula o comportamento de um modelo ou ferramenta real.
    """

    def __init__(self, name: str, response_template: str) -> None:
        super().__init__()
        self.connector_name = name
        self.response_template = response_template

    def initialize(self) -> None:
        """Inicializa o conector simulado."""
        self._is_initialized = True
        logger.info("Conector simulado '%s' inicializado com sucesso.", self.connector_name)

    def health_check(self) -> bool:
        """Verifica se o conector está operacional."""
        self._validate_initialization()
        return True

    def execute(self, **kwargs: Any) -> Any:
        """Executa a simulação processando o input recebido."""
        self._validate_initialization()
        input_data = kwargs.get("prompt", kwargs.get("text", ""))
        logger.info("Executando conector '%s' com input: '%s'", self.connector_name, input_data)
        return f"[{self.connector_name.upper()}] Processado: '{input_data}' -> {self.response_template}"


def main() -> None:
    """Função principal de execução do Assistente Operacional Universal."""
    logger.info("=== Inicializando: %s ===", settings.app_name)
    logger.info("Ambiente ativo: %s | Ollama URL: %s", settings.environment, settings.ollama_base_url)

    # 1. Instancia o Gerenciador de Inferência injetando as configurações globais
    inference_manager = InferenceManager(settings_instance=settings)

    # 2. Cria e registra conectores no InferenceManager (ex: Ollama e Fabric simulados)
    llm_connector = DummyAIIntegration("ollama", "Rascunho gerado com sucesso pelo modelo local.")
    analyzer_connector = DummyAIIntegration("fabric", "Análise estruturada e insights extraídos.")

    inference_manager.register_integration("ollama", llm_connector)
    inference_manager.register_integration("fabric", analyzer_connector)

    # 3. Configura o Orquestrador de Workflows
    orchestrator = WorkflowOrchestrator(inference_manager)

    # Adiciona etapas encadeadas ao workflow de forma fluente
    orchestrator.add_step(
        name="Gerar Conteúdo Base",
        integration_name="ollama",
        input_mapper=lambda ctx: {"prompt": f"Escreva um resumo sobre {ctx['tema']}"},
        output_key="rascunho",
    ).add_step(
        name="Refinar com Padrão Analítico",
        integration_name="fabric",
        input_mapper=lambda ctx: {"text": ctx["rascunho"]},
        output_key="analise_final",
    )

    # 4. Define os dados de entrada iniciais e executa o workflow
    contexto_inicial = {"tema": "Arquitetura Modular em Sistemas Multi-Agente"}
    
    logger.info("Iniciando execução do workflow orquestrado...")
    try:
        resultado_workflow = orchestrator.run(initial_context=contexto_inicial)

        print("\n" + "=" * 60)
        print("🎯 RESULTADO FINAL DO WORKFLOW ORQUESTRADO:")
        for chave, valor in resultado_workflow.items():
            print(f" • {chave}: {valor}")
        print("=" * 60 + "\n")

    except Exception as e:
        logger.error("Falha na execução do workflow principal: %s", str(e))


if __name__ == "__main__":
    main()
