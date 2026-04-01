"""
orchestrator.py — Maestro do sistema.

Recebe texto, decide o que fazer e coordena os módulos corretos.
É aqui que a mágica do fluxo acontece.
"""

from core.brain import generate_response
from core.memory import ConversationMemory
from actions.executor import execute
from config.settings import COMMAND_KEYWORDS, PERSONA_NAME


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
            return f"[{PERSONA_NAME}] Memória apagada. Recomeçando do zero."

        # ── Detecção de intenção ──────────────────────────────────────────────
        intent = detect_intent(text)

        if intent == "command":
            # Executa o comando e retorna o resultado diretamente
            result = execute(text)
            # Registra na memória como contexto (sem chamar a IA)
            self.memory.add_user(text)
            self.memory.add_assistant(result)
            return f"[Sistema] {result}"

        else:
            # Chat: passa para a IA com o histórico de contexto
            self.memory.add_user(text)
            response = generate_response(text, history=self.memory.get_history()[:-1])
            self.memory.add_assistant(response)
            return f"[{PERSONA_NAME}] {response}"
