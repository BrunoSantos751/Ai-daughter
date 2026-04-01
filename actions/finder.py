"""
finder.py — Busca dinâmica de executáveis no computador.

Quando o app não está registrado no COMMAND_MAP, este módulo
procura o .exe nos diretórios de instalação mais comuns do Windows.

Fluxo:
  1. Tenta shutil.which() no PATH do sistema (instantâneo)
  2. Busca nos diretórios comuns de instalação (limitado a _MAX_DEPTH)
  3. Retorna o caminho ou None se não encontrar

Cache em memória: apps já encontrados não são buscados de novo
na mesma sessão.
"""

import os
import shutil
from pathlib import Path


# ─── Configuração ──────────────────────────────────────────────────────────────

# Profundidade máxima de navegação dentro de cada diretório raiz.
# 4 cobre: ProgramFiles/<empresa>/<app>/subpasta/<app>.exe
_MAX_DEPTH = 4

# Diretórios raiz onde a maioria dos apps Windows se instala
_SEARCH_ROOTS: list[Path] = [
    # Instalações de sistema
    Path(os.environ.get("ProgramFiles",      r"C:\Program Files")),
    Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")),
    # Instalações por usuário (mais comuns hoje em dia)
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs",
    Path(os.environ.get("LOCALAPPDATA", "")),
    Path(os.environ.get("APPDATA", "")),
]

# Cache da sessão: evita varrer o disco duas vezes pro mesmo app
# Chave: nome normalizado | Valor: caminho encontrado ou None
_cache: dict[str, str | None] = {}


# ─── API pública ──────────────────────────────────────────────────────────────

def find_executable(app_name: str) -> str | None:
    """
    Procura um executável pelo nome no computador.

    Args:
        app_name: Nome do app (ex: "zen", "spotify", "discord")
                  Com ou sem extensão .exe.

    Returns:
        Caminho absoluto do executável, ou None se não encontrado.
    """
    key = app_name.lower().strip()

    # Verifica cache da sessão (não busca disco de novo)
    if key in _cache:
        return _cache[key]

    result = _search(key)
    _cache[key] = result  # salva no cache (mesmo que seja None)
    return result


def extract_app_name(text: str) -> str | None:
    """
    Extrai o nome do app de um comando em linguagem natural.

    Remove palavras de comando e artigos do início do texto,
    deixando apenas o nome do app que o usuário quer abrir.

    Exemplos:
        "abra o zen"           → "zen"
        "abrir o spotify"      → "spotify"
        "abre o visual studio" → "visual studio"
        "open discord"         → "discord"

    Args:
        text: Texto completo do comando do usuário.

    Returns:
        Nome extraído do app ou None se não conseguir extrair.
    """
    text_clean = text.lower().strip()

    # Palavras de comando para remover do início (do maior para o menor)
    command_prefixes = [
        "abrir o", "abrir a", "abra o", "abra a",
        "abre o", "abre a", "open the", "open",
        "executar o", "executar", "execute o", "execute",
        "iniciar o", "iniciar", "inicia o", "inicia",
        "rodar o", "rodar", "roda o", "roda",
        "ligar o", "ligar", "liga o", "liga",
        "abrir", "abra", "abre",
    ]

    remainder = text_clean
    for prefix in sorted(command_prefixes, key=len, reverse=True):
        if remainder.startswith(prefix):
            remainder = remainder[len(prefix):].strip()
            break

    # Remove artigos soltos no início ("o spotify" → "spotify")
    for article in ["o ", "a ", "os ", "as "]:
        if remainder.startswith(article):
            remainder = remainder[len(article):].strip()

    # Remove sufixos comuns ("pra mim", "para mim", "agora")
    noise_suffixes = [" pra mim", " para mim", " por favor", " agora", " please"]
    for suffix in noise_suffixes:
        if remainder.endswith(suffix):
            remainder = remainder[: -len(suffix)].strip()

    return remainder if remainder else None


# ─── Busca interna ────────────────────────────────────────────────────────────

def _search(name: str) -> str | None:
    """Executa a busca em camadas: PATH → diretórios comuns."""

    # ── Camada 1: PATH do sistema (shutil.which) ─────────────────────────────
    # Cobre apps instalados globalmente: git, ffmpeg, python, etc.
    for candidate in [name, f"{name}.exe"]:
        found = shutil.which(candidate)
        if found:
            return found

    # ── Camada 2: Diretórios de instalação ───────────────────────────────────
    exe_name = name if name.endswith(".exe") else f"{name}.exe"

    for root in _SEARCH_ROOTS:
        if not root.exists():
            continue
        result = _walk_limited(root, exe_name, depth=0)
        if result:
            return result

    return None


def _walk_limited(directory: Path, exe_name: str, depth: int) -> str | None:
    """
    Percorre um diretório procurando um executável, respeitando
    o limite de profundidade para não demorar demais.
    """
    if depth > _MAX_DEPTH:
        return None

    try:
        for entry in directory.iterdir():
            # Encontrou o arquivo?
            if entry.is_file() and entry.name.lower() == exe_name.lower():
                return str(entry)

            # É um diretório? Desce um nível
            if entry.is_dir():
                result = _walk_limited(entry, exe_name, depth + 1)
                if result:
                    return result

    except PermissionError:
        # Ignora pastas protegidas (WindowsApps, etc.)
        pass

    return None
