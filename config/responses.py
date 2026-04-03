"""
responses.py — Carrega e gerencia as respostas predefinidas do sistema.
"""

import json
from pathlib import Path
from config.settings import PERSONA_NAME

_BASE_DIR = Path(__file__).parent
_RESPONSES_FILE = _BASE_DIR / "responses.json"

with open(_RESPONSES_FILE, "r", encoding="utf-8") as f:
    _RESPONSES = json.load(f)

def get_response(path: str, **kwargs) -> str | list[str]:
    """
    Obtém uma resposta predefinida do arquivo responses.json.
    
    Args:
        path: Caminho separado por pontos (ex: 'errors.model_not_found').
        **kwargs: Variáveis para formatar na string.
        
    Returns:
        A string formatada ou lista de strings formatadas.
    """
    keys = path.split(".")
    data = _RESPONSES
    try:
        for key in keys:
            data = data[key]
    except KeyError:
        return f"Response mapping '{path}' not found."
        
    if "persona_name" not in kwargs:
        kwargs["persona_name"] = PERSONA_NAME

    if isinstance(data, list):
        return [item.format(**kwargs) for item in data]
    
    if isinstance(data, str):
        return data.format(**kwargs)
        
    return str(data)
