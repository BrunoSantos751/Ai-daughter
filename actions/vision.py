"""
vision.py — Responsável pela captura de tela e comunicação com o modelo de visão.
"""

import tempfile
import ollama
from pathlib import Path
from PIL import ImageGrab

from config.settings import OLLAMA_VISION_MODEL
from config.responses import get_response

def analyze_screen_with_moondream(user_prompt: str) -> str:
    """
    Captura a tela atual, envia para o Ollama (modelo Moondream) e retorna a descrição.

    Args:
        user_prompt: A frase dita pelo usuário ao solicitar a visão.

    Returns:
        O texto da análise gerada pelo Moondream.
    """
    tmp_path = ""
    try:
        # Captura a tela atual
        image = ImageGrab.grab()
        
        # Salva em um arquivo temporário
        fd, tmp_path = tempfile.mkstemp(suffix=".png")
        # Fecha o file descriptor para podermos usar o Pillow livremente
        import os
        os.close(fd)
        
        image.save(tmp_path, format="PNG")
        print(f"  🔍 (DEBUG) Imagem de visão salva temporariamente em: {tmp_path}")
        
        # Se o prompt estiver muito vazio, dá uma instrução base
        content_prompt = user_prompt.strip()
        if not content_prompt or len(content_prompt) < 3:
            content_prompt = "Descreva detalhadamente o que você está vendo nesta imagem."

        # Chama a API do moondream
        resp = ollama.chat(
            model=OLLAMA_VISION_MODEL,
            messages=[{
                "role": "user",
                "content": content_prompt,
                "images": [tmp_path]
            }],
            keep_alive="5m"  # Mantém por 5 minutos ativo na memória
        )
        
        return resp["message"]["content"].strip()

    except Exception as e:
        # Em caso de falha, captura e lança erro amigável
        return get_response("errors.moondream_failed", error=str(e))
    finally:
        # Tenta apagar o arquivo temporário
        """if tmp_path and Path(tmp_path).exists():
            try:
                Path(tmp_path).unlink()
            except Exception:
                pass"""
