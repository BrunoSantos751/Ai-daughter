"""
brain.py — Cérebro da Aiko.

Responsável por se comunicar com o Ollama (LLM local, gratuito)
e retornar respostas com a persona definida no system prompt.

Como funciona:
  - Ollama expõe uma API REST em http://localhost:11434
  - Usamos a biblioteca `ollama` que abstrai essa comunicação
  - Zero custo, zero internet, tudo roda na sua máquina
  - Retry automático quando o modelo ainda está carregando
  - Spinner animado no terminal enquanto aguarda a resposta
"""

import sys
import time
import threading
import ollama
from config.settings import OLLAMA_MODEL, SYSTEM_PROMPT, PERSONA_NAME, USE_BUILTIN_PERSONA

# Quantas vezes tentar se o modelo ainda estiver carregando
_MAX_RETRIES = 5
# Segundos entre cada tentativa
_RETRY_DELAY = 3.0
# Frames do spinner Braille
_SPIN_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


# ─── Spinner ──────────────────────────────────────────────────────────────────

def _chat_with_spinner(messages: list[dict]) -> str:
    """
    Chama ollama.chat() de forma bloqueante em uma thread separada
    enquanto exibe um spinner animado no terminal principal.

    O spinner desaparece automaticamente quando a resposta chega,
    sem deixar artefatos visuais na tela.

    Args:
        messages: Lista de mensagens no formato Ollama.

    Returns:
        Conteúdo da resposta como string.

    Raises:
        Propaga qualquer exceção lançada pelo Ollama (ResponseError, etc.)
    """
    stop_event = threading.Event()
    result: dict = {}
    error_box: list = []

    def _worker() -> None:
        try:
            resp = ollama.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                options={
                    "temperature": 0.8,  # Criatividade para a persona
                    "num_predict": 300,  # Equivalente a max_tokens
                },
            )
            result["content"] = resp["message"]["content"].strip()
        except Exception as exc:
            error_box.append(exc)
        finally:
            stop_event.set()

    worker_thread = threading.Thread(target=_worker, daemon=True)
    worker_thread.start()

    # Anima o spinner enquanto aguarda a thread terminar
    frame_idx = 0
    while not stop_event.is_set():
        frame = _SPIN_FRAMES[frame_idx % len(_SPIN_FRAMES)]
        sys.stdout.write(f"\r  {frame} {PERSONA_NAME} está pensando...")
        sys.stdout.flush()
        frame_idx += 1
        time.sleep(0.08)

    # Limpa a linha do spinner antes de imprimir a resposta
    sys.stdout.write("\r" + " " * 45 + "\r")
    sys.stdout.flush()

    worker_thread.join()

    # Re-propaga erros do Ollama para o retry handler em generate_response()
    if error_box:
        raise error_box[0]

    if "content" not in result:
        raise RuntimeError("Worker thread não retornou resultado.")

    return result["content"]


# ─── Interface pública ────────────────────────────────────────────────────────

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
    # Monta a lista de mensagens.
    # Se o modelo 'ai:daughter' está ativo, a persona já está embutida
    # via Modelfile — não precisa enviar o SYSTEM_PROMPT novamente.
    # Para modelos base (ex: gemma3:4b), envia o system prompt normal.
    messages: list[dict] = []
    if not USE_BUILTIN_PERSONA:
        messages.append({"role": "system", "content": SYSTEM_PROMPT})

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": text})

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            return _chat_with_spinner(messages)

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
