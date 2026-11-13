"""
Motor de Orquestração de Workflows (Core) - Assistente Operacional Universal
Utiliza logging estruturado para rastrear a execução de etapas multi-agente.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from core.inference.manager import InferenceManager
from core.logging import get_logger
from integrations.base import IntegrationError

logger = get_logger(__name__)


@dataclass
class WorkflowStep:
    name: str
    integration_name: str
    input_mapper: Callable[[Dict[str, Any]], Dict[str, Any]]
    output_key: str
    transform_output: Optional[Callable[[Any], Any]] = None


class WorkflowOrchestrator:
    """Orquestrador de fluxos multi-agente com logging estruturado."""

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
        step = WorkflowStep(
            name=name,
            integration_name=integration_name,
            input_mapper=input_mapper,
            output_key=output_key,
            transform_output=transform_output,
        )
        self.steps.append(step)
        logger.debug("Etapa adicionada ao workflow", step_name=name, integration=integration_name)
        return self

    def run(self, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.steps:
            logger.error("Tentativa de execução de workflow sem etapas")
            raise IntegrationError("O workflow não possui etapas configuradas para execução.")

        context: Dict[str, Any] = dict(initial_context) if initial_context else {}
        logger.info("Iniciando execução de workflow", total_steps=len(self.steps))

        for index, step in enumerate(self.steps, start=1):
            logger.info("Executando etapa do workflow", step_index=index, total=len(self.steps), step_name=step.name, integration=step.integration_name)
            try:
                step_kwargs = step.input_mapper(context)
                raw_result = self.inference_manager.execute(step.integration_name, **step_kwargs)
                processed_result = step.transform_output(raw_result) if step.transform_output else raw_result
                context[step.output_key] = processed_result
            except IntegrationError:
                raise
            except Exception as e:
                logger.error("Erro inesperado na etapa do workflow", step_name=step.name, error=str(e))
                raise IntegrationError(f"Falha na etapa '{step.name}' do workflow: {e}") from e

        logger.info("Workflow concluído com sucesso")
        return context
