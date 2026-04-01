"""
brain.py — Cérebro da Aiko.

Responsável por se comunicar com o Ollama (LLM local, gratuito)
e retornar respostas com a persona definida no system prompt.

Como funciona:
  - Ollama expõe uma API REST em http://localhost:11434
  - Usamos a biblioteca `ollama` que abstrai essa comunicação
  - Zero custo, zero internet, tudo roda na sua máquina
  - Retry automático quando o modelo ainda está carregando
"""

import time
import ollama
from config.settings import OLLAMA_MODEL, SYSTEM_PROMPT, PERSONA_NAME

# Quantas vezes tentar se o modelo ainda estiver carregando
_MAX_RETRIES = 5
# Segundos entre cada tentativa
_RETRY_DELAY = 3.0


def generate_response(text: str, history: list[dict] | None = None) -> str:
    """
    Envia o texto do usuário para o modelo local via Ollama
    e retorna a resposta da Aiko.

    Inclui retry automático para quando o Ollama ainda está carregando
    o modelo na memória (erro 500 "llm server loading model").

    Args:
        text:    Mensagem do usuário.
        history: Histórico opcional de mensagens anteriores para contexto.

    Returns:
        Resposta do modelo como string.
    """
    # Monta a lista de mensagens: [system] + [histórico] + [mensagem atual]
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": text})

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                options={
                    "temperature": 0.8,  # Criatividade para a persona
                    "num_predict": 300,  # Equivalente a max_tokens
                },
            )
            return response["message"]["content"].strip()

        except ollama.ResponseError as e:
            error_msg = str(e).lower()

            # Modelo ainda carregando — aguarda e tenta de novo
            if "loading" in error_msg or "status code: 500" in error_msg:
                if attempt < _MAX_RETRIES:
                    print(
                        f"  ⏳ Modelo carregando... aguardando "
                        f"({attempt}/{_MAX_RETRIES})"
                    )
                    time.sleep(_RETRY_DELAY)
                    continue
                else:
                    return (
                        "O modelo demorou demais para carregar. "
                        "Tente novamente em alguns segundos."
                    )

            # Modelo não encontrado — instrui o usuário a baixar
            if "not found" in error_msg or "pull" in error_msg:
                return (
                    f"Modelo '{OLLAMA_MODEL}' não encontrado. "
                    f"Rode: ollama pull {OLLAMA_MODEL}"
                )

            return f"Erro do Ollama: {e}"

        except Exception:
            # Ollama provavelmente não está rodando
            return (
                "Não consegui conectar ao Ollama. "
                "Verifique se ele está rodando: ollama serve"
            )

    return "Não foi possível obter resposta após várias tentativas."
