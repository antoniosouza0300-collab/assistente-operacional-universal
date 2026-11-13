"""
Interface Web Gradio - Assistente Operacional Universal
Permite interagir com os modelos e fluxos de IA de forma visual.
"""

import gradio as gr
from config.settings import Settings
from core.inference.manager import InferenceManager
from integrations.ollama.client import OllamaIntegration

# 1. Configuração inicial do core
settings = Settings()
manager = InferenceManager(settings)

# 2. Inicialização e registro do conector Ollama
ollama_config = {
    "base_url": "http://localhost:11434",
    "default_model": "llama3",
    "timeout": 30,
    "max_retries": 3
}
ollama_client = OllamaIntegration(ollama_config)
ollama_client.initialize()
manager.register_integration("ollama", ollama_client)

def processar_solicitacao(prompt: str, modelo: str):
    """Função de ponte entre a interface do Gradio e o InferenceManager."""
    if not prompt.strip():
        return "Por favor, insira um prompt válido."
    
    try:
        resposta = manager.execute("ollama", prompt=prompt, model=modelo)
        return resposta
    except Exception as e:
        return f"Erro durante a execução da inferência: {str(e)}"

# 3. Construção da Interface com Gradio Blocks
with gr.Blocks(title="Assistente Operacional Universal") as demo:
    gr.Markdown("# 🤖 Assistente Operacional Universal")
    gr.Markdown("Interface web modular para orquestração de agentes e inferências de IA.")
    
    with gr.Row():
        with gr.Column(scale=2):
            prompt_input = gr.Textbox(
                label="Prompt / Tarefa", 
                placeholder="Ex: Escreva um script em Python para validar dados com Pydantic...",
                lines=5
            )
            model_input = gr.Textbox(
                label="Modelo", 
                value="llama3",
                info="Nome do modelo configurado no Ollama"
            )
            submit_btn = gr.Button("Executar Inferência", variant="primary")
            
        with gr.Column(scale=3):
            output_box = gr.Textbox(
                label="Resultado da Execução", 
                lines=14
            )

    submit_btn.click(
        fn=processar_solicitacao,
        inputs=[prompt_input, model_input],
        outputs=output_box
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
