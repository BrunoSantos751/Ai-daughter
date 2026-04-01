"""
commands.py — Definição de comandos e apelidos disponíveis.

Centraliza quais apps/ações o sistema conhece. O executor consulta
esse mapeamento para saber o que rodar.

Para adicionar um apelido novo, edite o dict ALIASES abaixo:
    "meu apelido": "nome real do app"
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


# ─── Apelidos ─────────────────────────────────────────────────────────────────
# Mapeamento de apelido → nome real do app.
# O nome real é passado para o finder, que busca o executável no computador.
#
# Para adicionar: "meu apelido": "nome do executável ou app"

ALIASES: dict[str, str] = {
    "navegador":        "zen",
    "browser":          "zen",
    "codigo":           "vscode",
    "editor":           "vscode",
    "editor de codigo": "vscode",
    "musica":           "spotify",
    "chat":             "discord",
    "jogos":            "steam",
    "terminal":         "wt",        # Windows Terminal
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


def resolve_alias(app_name: str) -> str | None:
    """
    Verifica se o nome extraído é um apelido e retorna o nome real.

    Exemplos:
        "navegador" → "zen"
        "browser"   → "zen"
        "codigo"    → "vscode"

    Args:
        app_name: Nome extraído do comando do usuário (lowercase).

    Returns:
        Nome real do app, ou None se não for um apelido conhecido.
    """
    return ALIASES.get(app_name.lower().strip())
