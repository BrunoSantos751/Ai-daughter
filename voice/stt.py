"""
stt.py — Speech-to-Text via faster-whisper e sounddevice.

Permite gravação do microfone (Push-to-Talk) e 
transcrição do áudio para texto localmente usando o modelo Whisper.
"""

import sys
import os
import json
import queue
import tempfile
import threading
import warnings
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel

from config.settings import WHISPER_MODEL, STT_RATE

# Suprime lixo do log se houver
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

_model = None
_q = queue.Queue()
_recording = False
_stt_context = ""

def _load_context():
    """Carrega o contexto (initial prompt) do JSON"""
    global _stt_context
    try:
        with open(os.path.join("config", "stt_context.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
            _stt_context = data.get("initial_prompt", "")
    except Exception:
        _stt_context = ""


def _audio_callback(indata, frames, time, status):
    """Callback do sounddevice chamado para cada bloco de áudio gravado."""
    if status:
        print(status, file=sys.stderr)
    if _recording:
        _q.put(indata.copy())


def record_until_enter(samplerate: int = STT_RATE, channels: int = 1) -> str | None:
    """
    Inicia a gravação no microfone padrão.
    O terminal fica aguardando o usuário pressionar Enter para parar a gravação.

    Returns:
        String com o caminho para o arquivo WAV temporário, ou None se falhou.
    """
    global _recording
    
    # Limpa a fila antes de começar
    while not _q.empty():
        _q.get()

    _recording = True
    print("\n🎤  [Voz] Gravando... (Pressione ENTER para terminar) ", end="", flush=True)

    try:
        with sd.InputStream(samplerate=samplerate, channels=channels, callback=_audio_callback):
            input()  # Bloqueia até o usuário dar Enter
            _recording = False
    except Exception as e:
        print(f"\n❌ Erro ao acessar o microfone: {e}")
        _recording = False
        return None

    print("⏳  [Voz] Adquirindo e salvando áudio... ", end="\r", flush=True)

    audio_chunks = []
    while not _q.empty():
        audio_chunks.append(_q.get())

    if not audio_chunks:
        return None

    audio_np = np.concatenate(audio_chunks, axis=0)

    # Cria arquivo temporário
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".wav")
    os.close(tmp_fd)

    wav.write(tmp_path, samplerate, audio_np)
    return tmp_path


def load_model():
    """Carrega o modelo do Whisper na memória sob demanda."""
    global _model
    if _model is None:
        print(f"⏳  [Voz] Carregando modelo STT '{WHISPER_MODEL}' via faster-whisper...")
        _load_context()
        # Usamos int8 para garantir compatibilidade e alta velocidade sem o warning de FP16 do ctranslate2
        _model = WhisperModel(WHISPER_MODEL, device="auto", compute_type="int8")


def transcribe(audio_path: str) -> str:
    """
    Transcreve um arquivo de áudio temporário para texto.

    Args:
        audio_path: Caminho para o arquivo WAV.

    Returns:
        Texto transcrito contendo o comando/mensagem do usuário.
    """
    load_model()
    
    # Faz a transcrição propriamente dita
    segments, info = _model.transcribe(
        audio_path, 
        language="pt",
        initial_prompt=_stt_context if _stt_context else None
    )
    
    text = "".join([segment.text for segment in segments])
    
    # Apaga o arquivo temporário pois não precisamos mais dele
    try:
        os.remove(audio_path)
    except OSError:
        pass
        
    return text.strip()
