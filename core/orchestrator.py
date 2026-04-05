"""
orchestrator.py — Maestro do sistema.

Recebe texto, decide o que fazer e coordena os módulos corretos.
É aqui que a mágica do fluxo acontece.
"""

from core.brain import generate_response
from core.memory import ConversationMemory
from actions.executor import execute
from config.settings import COMMAND_KEYWORDS, VISION_KEYWORDS, PERSONA_NAME
from config.responses import get_response


def detect_intent(text: str) -> str:
    """
    Detecta se o texto do usuário é um comando ou uma conversa.

    Estratégia simples baseada em palavras-chave.
    No futuro, isso pode ser substituído por classificação via IA.

    Args:
        text: Texto do usuário.

    Returns:
        "command" se parecer um comando, "chat" caso contrário.
    """
    text_lower = text.lower().strip()

    for keyword in VISION_KEYWORDS:
        if text_lower.startswith(keyword) or f" {keyword} " in text_lower:
            return "vision"

    for keyword in COMMAND_KEYWORDS:
        if text_lower.startswith(keyword) or f" {keyword} " in text_lower:
            return "command"

    return "chat"


class Orchestrator:
    """
    Coordena o fluxo completo de uma interação:
    texto → intenção → ação (execução ou resposta de IA).
    """

    def __init__(self) -> None:
        self.memory = ConversationMemory(max_turns=10)

    def handle(self, user_input: str) -> str:
        """
        Processa uma entrada do usuário e retorna a resposta final.

        Fluxo:
          1. Detecta a intenção (command vs chat)
          2. Se comando → executa e retorna feedback
          3. Se chat → consulta a IA com contexto de memória

        Args:
            user_input: Texto digitado pelo usuário.

        Returns:
            Resposta para exibir no terminal.
        """
        text = user_input.strip()

        if not text:
            return ""

        # Comandos especiais da sessão
        if text.lower() in ("limpar", "clear", "esquece tudo"):
            self.memory.clear()
            return get_response("system.memory_cleared")

        # ── Detecção de intenção ──────────────────────────────────────────────
        intent = detect_intent(text)

        if intent == "vision":
            from actions.vision import analyze_screen_with_moondream
            
            # Feedback temporário no terminal
            print(get_response("system.taking_screenshot"))
            
            # Análise da tela pelo moondream
            analysis_result = analyze_screen_with_moondream(text)
            
            # Contexto (usuário)
            self.memory.add_user(text)
            temp_history = self.memory.get_history()[:-1]
            
            # Prompt enriquecido para a Saphira
            prompt = get_response("system.vision_prompt", text=text, analysis=analysis_result)
            
            response = generate_response(prompt, history=temp_history)
            self.memory.add_assistant(response)
            
            return f"[{PERSONA_NAME}] {response}"

        elif intent == "command":
            # Executa o comando e obtém o resultado do sistema
            result = execute(text)
            
            # Registra o comando do usuário na memória
            self.memory.add_user(text)
            
            # Pega o histórico atual e remove o último item (que é a mensagem atual)
            # para substituí-la por uma versão com o feedback do sistema embutido.
            temp_history = self.memory.get_history()[:-1]
            
            # Cria um prompt enriquecido para a IA gerar a resposta
            prompt = get_response("system.command_executed_prompt", text=text, result=result)
            
            # Passa para a IA com o histórico de contexto
            response = generate_response(prompt, history=temp_history)
            self.memory.add_assistant(response)
            
            return f"[{PERSONA_NAME}] {response}"

        else:
            # Chat: passa para a IA com o histórico de contexto
            self.memory.add_user(text)
            response = generate_response(text, history=self.memory.get_history()[:-1])
            self.memory.add_assistant(response)
            return f"[{PERSONA_NAME}] {response}"
