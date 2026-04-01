"""
memory.py — Memória de conversa da sessão atual.

Mantém o histórico de mensagens para que a Aiko se lembre do contexto
enquanto o programa estiver rodando (memória em RAM, não persistente).
"""

from dataclasses import dataclass, field


@dataclass
class ConversationMemory:
    """
    Armazena o histórico de turnos da conversa atual.

    Attributes:
        max_turns: Máximo de pares (usuário + assistente) mantidos.
                   Evita enviar contexto gigante para a API.
    """
    max_turns: int = 10
    _history: list[dict] = field(default_factory=list)

    def add_user(self, text: str) -> None:
        """Registra uma mensagem do usuário."""
        self._history.append({"role": "user", "content": text})
        self._trim()

    def add_assistant(self, text: str) -> None:
        """Registra uma resposta do assistente."""
        self._history.append({"role": "assistant", "content": text})
        self._trim()

    def get_history(self) -> list[dict]:
        """Retorna o histórico atual (sem o system prompt)."""
        return list(self._history)

    def clear(self) -> None:
        """Apaga toda a memória da sessão."""
        self._history.clear()

    def _trim(self) -> None:
        """
        Mantém apenas os últimos N pares de mensagens.
        Cada 'par' = 1 mensagem user + 1 assistente = 2 itens.
        """
        max_items = self.max_turns * 2
        if len(self._history) > max_items:
            self._history = self._history[-max_items:]

    def __len__(self) -> int:
        return len(self._history)
