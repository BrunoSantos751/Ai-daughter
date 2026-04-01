"""
executor.py — Executa ações no sistema operacional.

Recebe um comando resolvido (dict) e realiza a ação correspondente.
Atualmente suporta: abrir aplicativos.
"""

import subprocess
from pathlib import Path
from actions.commands import resolve_command


def execute(text: str) -> str:
    """
    Ponto de entrada principal do executor.

    Tenta resolver o texto em um comando conhecido e executá-lo.

    Args:
        text: Texto bruto do usuário (ex: "abre o chrome pra mim").

    Returns:
        Mensagem de feedback para exibir ao usuário.
    """
    command = resolve_command(text)

    if command is None:
        return "Entendi que é um comando, mas não sei o que fazer com isso ainda."

    # Despacha para o handler correto com base no tipo
    handlers = {
        "open_app": _open_app,
    }

    handler = handlers.get(command["type"])
    if handler:
        return handler(command)

    return f"Tipo de comando '{command['type']}' ainda não implementado."


# ─── Handlers internos ────────────────────────────────────────────────────────

def _open_app(command: dict) -> str:
    """
    Abre um aplicativo pelo caminho do executável.

    Usa subprocess.Popen para não bloquear o loop principal.
    """
    path = command["path"]
    label = command.get("label", path)

    # Verifica se o executável existe antes de tentar abrir
    # (aceita tanto caminhos absolutos quanto comandos do PATH do sistema)
    path_obj = Path(path)
    if not path_obj.is_absolute() or path_obj.exists():
        try:
            subprocess.Popen(
                path,
                shell=True,          # shell=True permite executáveis do PATH
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return f"Abrindo {label}..."
        except Exception as e:
            return f"Não consegui abrir {label}. Erro: {e}"
    else:
        return (
            f"Não encontrei o executável de {label} em: {path}\n"
            f"Verifique o caminho em config/settings.py → APP_PATHS"
        )
