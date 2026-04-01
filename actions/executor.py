"""
executor.py — Executa ações no sistema operacional.

Fluxo de resolução de um comando:
  1. Verifica COMMAND_MAP (apps pré-cadastrados) — instantâneo
  2. Se não encontrar, busca dinamicamente no computador via finder.py
  3. Se ainda não achar, retorna mensagem ao usuário
"""

import subprocess
from pathlib import Path

from actions.commands import resolve_command
from actions.finder import find_executable, extract_app_name


def execute(text: str) -> str:
    """
    Ponto de entrada principal do executor.

    Tenta resolver o comando pelo COMMAND_MAP primeiro e, se não achar,
    faz uma busca dinâmica no sistema de arquivos.

    Args:
        text: Texto bruto do usuário (ex: "abre o zen browser").

    Returns:
        Mensagem de feedback para exibir ao usuário.
    """
    # ── Etapa 1: apps pré-cadastrados (rápido) ────────────────────────────────
    command = resolve_command(text)
    if command is not None:
        return _dispatch(command)

    # ── Etapa 2: busca dinâmica no computador ─────────────────────────────────
    app_name = extract_app_name(text)

    if not app_name:
        return "Entendi que é um comando, mas não consegui identificar o app."

    print(f"  🔍 Procurando '{app_name}' no computador...")

    exe_path = find_executable(app_name)

    if exe_path:
        return _launch(exe_path, label=app_name.title())
    else:
        return (
            f"Procurei por '{app_name}' mas não encontrei nada. "
            f"Verifique se está instalado ou adicione em config/settings.py → APP_PATHS."
        )


# ─── Dispatcher e handlers ────────────────────────────────────────────────────

def _dispatch(command: dict) -> str:
    """Despacha para o handler correto com base no tipo do comando."""
    handlers = {
        "open_app": lambda cmd: _launch(cmd["path"], cmd.get("label", cmd["path"])),
    }
    handler = handlers.get(command["type"])
    if handler:
        return handler(command)
    return f"Tipo de comando '{command['type']}' ainda não implementado."


def _launch(path: str, label: str) -> str:
    """
    Abre um executável via subprocess sem bloquear o loop principal.

    Args:
        path:  Caminho do executável (absoluto ou no PATH).
        label: Nome amigável para exibir ao usuário.
    """
    path_obj = Path(path)

    # Aceita: caminhos absolutos existentes OU comandos do PATH (ex: "notepad.exe")
    if not path_obj.is_absolute() or path_obj.exists():
        try:
            subprocess.Popen(
                path,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return f"Abrindo {label}..."
        except Exception as e:
            return f"Não consegui abrir {label}. Erro: {e}"
    else:
        return f"Executável não encontrado em: {path}"
