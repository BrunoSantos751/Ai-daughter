"""
executor.py — Executa ações no sistema operacional.

Fluxo de resolução de um comando:
  1. Verifica COMMAND_MAP (apps pré-cadastrados) — instantâneo
  2. Se não encontrar, busca dinamicamente no computador via finder.py
  3. Se ainda não achar, retorna mensagem ao usuário
"""

import subprocess
from pathlib import Path

from actions.commands import resolve_command, resolve_alias
from actions.finder import find_executable, extract_app_name
from config.responses import get_response


_last_phrase: str = ""


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

    app_name = extract_app_name(text)

    if not app_name:
        return get_response("errors.unidentified_app")

    # ── Etapa 2: resolve apelidos ("navegador" → "zen") ───────────────────────
    real_name = resolve_alias(app_name)
    if real_name:
        app_name = real_name

    # ── Etapa 3: busca dinâmica no computador ─────────────────────────────────
    global _last_phrase
    import random
    
    phrases = get_response("searching", app_name=app_name)
    
    available_phrases = [p for p in phrases if p != _last_phrase]
    chosen = random.choice(available_phrases) if available_phrases else random.choice(phrases)
    _last_phrase = chosen
    print(f"{chosen}")

    exe_path = find_executable(app_name)

    if exe_path:
        return _launch(exe_path, label=app_name.title())
    else:
        return get_response("errors.app_not_found", app_name=app_name)


# ─── Dispatcher e handlers ────────────────────────────────────────────────────

def _dispatch(command: dict) -> str:
    """Despacha para o handler correto com base no tipo do comando."""
    handlers = {
        "open_app": lambda cmd: _launch(cmd["path"], cmd.get("label", cmd["path"])),
    }
    handler = handlers.get(command["type"])
    if handler:
        return handler(command)
    return get_response("errors.command_not_implemented", command_type=command["type"])


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
            return get_response("success.opening_app", label=label)
        except Exception as e:
            return get_response("errors.failed_to_open", label=label, error=e)
    else:
        return get_response("errors.executable_not_found", label=label, path=path)
