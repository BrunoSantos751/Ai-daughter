"""
commands.py — Definição de comandos disponíveis.

Centraliza quais apps/ações o sistema conhece. O executor consulta
esse mapeamento para saber o que rodar.
"""

from config.settings import APP_PATHS


# ─── Mapeamento de intenção → ação executável ─────────────────────────────────
# Chave: fragmento que aparece no texto do usuário (lowercase)
# Valor: dicionário com o tipo de ação e os dados necessários

COMMAND_MAP: dict[str, dict] = {
    # ── Aplicativos ───────────────────────────────────────────────────────────
    "chrome": {
        "type": "open_app",
        "path": APP_PATHS["chrome"],
        "label": "Google Chrome",
    },
    "google chrome": {
        "type": "open_app",
        "path": APP_PATHS["chrome"],
        "label": "Google Chrome",
    },
    "vscode": {
        "type": "open_app",
        "path": APP_PATHS["vscode"],
        "label": "VS Code",
    },
    "vs code": {
        "type": "open_app",
        "path": APP_PATHS["vscode"],
        "label": "VS Code",
    },
    "visual studio code": {
        "type": "open_app",
        "path": APP_PATHS["vscode"],
        "label": "VS Code",
    },
    "bloco de notas": {
        "type": "open_app",
        "path": APP_PATHS["notepad"],
        "label": "Bloco de Notas",
    },
    "notepad": {
        "type": "open_app",
        "path": APP_PATHS["notepad"],
        "label": "Bloco de Notas",
    },
    "explorador": {
        "type": "open_app",
        "path": APP_PATHS["explorer"],
        "label": "Explorador de Arquivos",
    },
    "explorador de arquivos": {
        "type": "open_app",
        "path": APP_PATHS["explorer"],
        "label": "Explorador de Arquivos",
    },
}


def resolve_command(text: str) -> dict | None:
    """
    Tenta encontrar um comando no texto do usuário.

    Varre o COMMAND_MAP procurando qualquer chave que apareça no texto.
    Retorna o comando correspondente ou None se não encontrar nada.

    Args:
        text: Texto do usuário em lowercase.

    Returns:
        Dicionário do comando ou None.
    """
    text_lower = text.lower()
    for keyword, command in COMMAND_MAP.items():
        if keyword in text_lower:
            return command
    return None
