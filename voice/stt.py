"""
stt.py — Speech-to-Text via RealtimeSTT.

Permite captura de microfone com Voice Activity Detection (VAD)
e transcrição do áudio para texto localmente usando o modelo Whisper.
"""

import sys
import os
import json

from config.settings import WHISPER_MODEL

# Para evitar problemas de libs conflitantes em alguns ambientes
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from RealtimeSTT import AudioToTextRecorder

_recorder = None
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

def load_model():
    """Carrega e inicializa o RealtimeSTT sob demanda."""
    global _recorder
    if _recorder is None:
        print(f"⏳  [Voz] Inicializando RealtimeSTT (modelo: '{WHISPER_MODEL}')...")
        _load_context()
        
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
    Inicia e aguarda a fala utilizando VAD (Voice Activity Detection).
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
