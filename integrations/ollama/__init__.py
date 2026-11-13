"""
Submódulo de Integração Ollama - Assistente Operacional Universal
Expõe o conector Ollama para inferência local.
"""

from integrations.ollama.client import OllamaIntegration

__all__ = ["OllamaIntegration"]
