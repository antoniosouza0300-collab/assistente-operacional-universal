"""
Motor de Orquestração de Workflows (Core) - Assistente Operacional Universal
Permite encadear execuções entre múltiplos conectores e agentes de forma sequencial,
propagando estado e transformando saídas entre etapas.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from core.inference.manager import InferenceManager
from integrations.base import IntegrationError

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    """
    Representa uma etapa individual dentro de um workflow orquestrado.
    """
    name: str
    integration_name: str
    input_mapper: Callable[[Dict[str, Any]], Dict[str, Any]]
    output_key: str
    transform_output: Optional[Callable[[Any], Any]] = None


class WorkflowOrchestrator:
    """
    Orquestrador de fluxos de trabalho multi-agente/multi-modelo.
    Executa uma sequência de WorkflowSteps utilizando o InferenceManager.
    """

    def __init__(self, inference_manager: InferenceManager) -> None:
        self.inference_manager = inference_manager
        self.steps: List[WorkflowStep] = []

    def add_step(
        self,
        name: str,
        integration_name: str,
        input_mapper: Callable[[Dict[str, Any]], Dict[str, Any]],
        output_key: str,
        transform_output: Optional[Callable[[Any], Any]] = None,
    ) -> "WorkflowOrchestrator":
        """
        Adiciona uma etapa ao pipeline de execução (interface fluente).
        
        Args:
            name: Nome descritivo da etapa.
            integration_name: Nome do conector registrado no InferenceManager.
            input_mapper: Função que recebe o contexto atual e retorna os kwargs para execute().
            output_key: Chave onde o resultado desta etapa será salvo no contexto.
            transform_output: Função opcional para extrair/formatar o retorno bruto do conector.
        """
        step = WorkflowStep(
            name=name,
            integration_name=integration_name,
            input_mapper=input_mapper,
            output_key=output_key,
            transform_output=transform_output,
        )
        self.steps.append(step)
        logger.debug("Etapa '%s' adicionada ao workflow (conector: %s).", name, integration_name)
        return self

    def run(self, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa todas as etapas registradas em sequência, acumulando os resultados no contexto.
        
        Args:
            initial_context: Dicionário inicial com os dados de entrada do workflow.
            
        Returns:
            Dict[str, Any]: Contexto final contendo os dados iniciais e todas as saídas geradas.
        """
        if not self.steps:
            raise IntegrationError("O workflow não possui etapas configuradas para execução.")

        context: Dict[str, Any] = dict(initial_context) if initial_context else {}
        logger.info("Iniciando execução de workflow com %d etapa(s).", len(self.steps))

        for index, step in enumerate(self.steps, start=1):
            logger.info("[%d/%d] Executando etapa '%s' via '%s'...", index, len(self.steps), step.name, step.integration_name)
            try:
                step_kwargs = step.input_mapper(context)
                raw_result = self.inference_manager.execute(step.integration_name, **step_kwargs)
                processed_result = step.transform_output(raw_result) if step.transform_output else raw_result
                context[step.output_key] = processed_result
            except IntegrationError:
                raise
            except Exception as e:
                logger.error("Erro inesperado na etapa '%s': %s", step.name, str(e))
                raise IntegrationError(f"Falha na etapa '{step.name}' do workflow: {e}") from e

        logger.info("Workflow concluído com sucesso.")
        return context
