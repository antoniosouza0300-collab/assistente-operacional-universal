"""
Interface de Linha de Comando (CLI) - Assistente Operacional Universal
Permite executar workflows orquestrados diretamente pelo terminal utilizando parâmetros customizáveis.
"""

import argparse
import logging
import sys

from config.settings import settings
from core.inference.manager import InferenceManager
from core.orchestrator.engine import WorkflowOrchestrator
from main import DummyAIIntegration

# Configuração de logging estruturado
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Configura e retorna o analisador de argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="CLI do Assistente Operacional Universal - Orquestração de Workflows"
    )
    parser.add_argument(
        "--topic",
        type=str,
        default="Sistemas Multi-Agente e Arquiteturas Modulares",
        help="Tema ou entrada principal a ser processada pelo workflow.",
    )
    parser.add_argument(
        "--env",
        type=str,
        default=settings.environment,
        help="Define o ambiente de execução (ex: development, production).",
    )
    return parser


def main() -> None:
    """Ponto de entrada do utilitário de linha de comando."""
    parser = create_parser()
    args = parser.parse_args()

    logger.info("=== Iniciando CLI (Ambiente: %s) ===", args.env)

    # 1. Inicializa o gerenciador de inferência com as configurações globais
    inference_manager = InferenceManager(settings_instance=settings)

    # 2. Registra os conectores (reutilizando a classe de demonstração do main.py)
    llm_connector = DummyAIIntegration("ollama", "Rascunho técnico gerado via CLI.")
    analyzer_connector = DummyAIIntegration("fabric", "Insights extraídos e estruturados via CLI.")

    inference_manager.register_integration("ollama", llm_connector)
    inference_manager.register_integration("fabric", analyzer_connector)

    # 3. Configura o workflow encadeado
    orchestrator = WorkflowOrchestrator(inference_manager)
    orchestrator.add_step(
        name="Gerar Conteúdo Inicial",
        integration_name="ollama",
        input_mapper=lambda ctx: {"prompt": f"Elabore um guia sobre: {ctx['topic']}"},
        output_key="rascunho",
    ).add_step(
        name="Aplicar Padrão Analítico",
        integration_name="fabric",
        input_mapper=lambda ctx: {"text": ctx["rascunho"]},
        output_key="analise_final",
    )

    # 4. Executa o workflow com o tópico fornecido via CLI
    try:
        contexto_inicial = {"topic": args.topic}
        logger.info("Executando workflow para o tópico: '%s'...", args.topic)
        
        resultado = orchestrator.run(initial_context=contexto_inicial)

        print("\n" + "=" * 65)
        print("🚀 RESULTADO DA EXECUÇÃO VIA CLI:")
        for chave, valor in resultado.items():
            print(f" • {chave}: {valor}")
        print("=" * 65 + "\n")

    except Exception as e:
        logger.error("Erro crítico na execução do CLI: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
