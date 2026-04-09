"""
stt.py — Speech-to-Text via RealtimeSTT.

Permite captura de microfone com Voice Activity Detection (VAD)
e transcrição do áudio para texto localmente usando o modelo Whisper.

Suporte a modo contínuo: o microfone fica sempre ativo e escuta
a próxima fala automaticamente enquanto o sistema processa a anterior.
"""

import sys
import os
import json
import threading
from queue import Queue, Empty

from config.settings import WHISPER_MODEL

# Para evitar problemas de libs conflitantes em alguns ambientes
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

_recorder = None
_stt_context = ""

# Estado do modo contínuo
_continuous_mode = False
_audio_ready = threading.Event()
_transcription_queue: Queue[str | None] = Queue()
_listen_thread: threading.Thread | None = None

def _load_context():
    """Carrega o contexto (initial prompt) do JSON"""
    global _stt_context
    try:
        with open(os.path.join("config", "stt_context.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
            _stt_context = data.get("initial_prompt", "")
    except Exception:
        _stt_context = ""

def load_model():
    """Carrega e inicializa o RealtimeSTT sob demanda."""
    global _recorder
    if _recorder is None:
        print(f"⏳  [Voz] Inicializando RealtimeSTT (modelo: '{WHISPER_MODEL}')...")
        _load_context()

        # Fazemos o import aqui dentro para não travar a inicialização do programa inteiro
        from RealtimeSTT import AudioToTextRecorder

        # Callback para ir printando o que for falado em tempo real
        def _process_text_realtime(text):
            sys.stdout.write(f"\rVocê (Voz) › {text}")
            sys.stdout.flush()

        # O RealtimeSTT descobre a CPU / GPU automaticamente e faz o download se não existir o modelo.
        # Desligamos o log intensivo para manter o terminal limpo
        import logging
        _recorder = AudioToTextRecorder(
            model=WHISPER_MODEL,
            language="pt",
            enable_realtime_transcription=True,
            on_realtime_transcription_update=_process_text_realtime,
            initial_prompt=_stt_context if _stt_context else None,
            device="cpu",             # Forçando CPU conforme solicitado
            compute_type="int8",      # Int8 garante alta performance em CPU
            level=logging.ERROR       # Logs silenciosos
        )
        sys.stdout.write("\r                                                   \r")
        sys.stdout.flush()

def get_voice_input() -> str:
    """
    Modo pontual: inicia e aguarda uma única fala utilizando VAD.
    A detecção entende o início e o término da fala sem precisar de botão.
    """
    load_model()

    print("\n🎤  [Voz] Fale agora... (aguardando falar) ", flush=True)

    # Bloqueia até a pessoa parar de falar (conforme VAD)
    text = _recorder.text()

    # Limpa a linha de transcrição pro retorno limpo
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()

    return text.strip() if text else ""


# ─── Modo contínuo ────────────────────────────────────────────────────────────

def _listen_loop():
    """Loop em background que capta falas e as coloca na fila."""
    while _continuous_mode:
        _audio_ready.wait()  # aguarda sinal de que pode escutar
        _audio_ready.clear()

        # Limpa a linha antes de mostrar o indicador de escuta
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()

        print("\n🎤  [Voz] Fale agora... (aguardando) ", flush=True)

        try:
            text = _recorder.text()
        except Exception:
            _transcription_queue.put(None)
            break

        # Limpa a linha de transcrição
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()

        if text and text.strip():
            _transcription_queue.put(text.strip())
        else:
            _transcription_queue.put(None)


def start_continuous_voice():
    """
    Entra no modo voz contínuo.
    O microfone fica sempre ativo e escuta a próxima fala
    automaticamente após o sistema processar a anterior.

    Use next(generator) para esperar a próxima fala,
    ou chame stop_continuous_voice() para encerrar.
    """
    global _continuous_mode, _listen_thread

    load_model()
    _continuous_mode = True
    _audio_ready.set()  # já começa escutando

    _listen_thread = threading.Thread(target=_listen_loop, daemon=True)
    _listen_thread.start()

    print("\n🎙️  [Modo contínuo] Fale à vontade. Microfone sempre ativo.")
    print("   Diga 'sair' após uma resposta para sair do modo voz.\n")


def wait_for_next_speech() -> str | None:
    """
    Aguarda a próxima fala transcrita. Retorna o texto ou None
    se o áudio estiver vazio.
    """
    try:
        return _transcription_queue.get(timeout=120)
    except Empty:
        return None


def signal_ready_for_next():
    """Sinaliza que o sistema está pronto para captar a próxima fala."""
    _audio_ready.set()


def stop_continuous_voice():
    """Encerra o modo contínuo e limpa recursos."""
    global _continuous_mode

    _continuous_mode = False
    _audio_ready.set()  # destrava a thread caso esteja esperando

    # Drena e sinaliza parada
    while not _transcription_queue.empty():
        try:
            _transcription_queue.get_nowait()
        except Empty:
            break
    _transcription_queue.put(None)

    if _listen_thread:
        _listen_thread.join(timeout=3)

    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()
