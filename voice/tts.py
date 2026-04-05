"""
tts.py — Text-to-Speech usando RealtimeTTS e Azure.

Implementa uma fila para garantir que falas sucessivas aguardem a
anterior terminar, evitando sobreposição de áudio.
"""

import threading
import queue
from config.settings import TTS_ENABLED, AZURE_SPEECH_KEY, AZURE_SPEECH_REGION, AZURE_SPEECH_VOICE

_engine = None
_stream = None
_tts_queue = queue.Queue()
_worker_thread = None

def _tts_worker():
    """Consome a fila de textos e fala sequencialmente."""
    import traceback
    while True:
        text = _tts_queue.get()
        if text is None:  # Sinal de parada da thread
            break
        try:
            if _stream:
                _stream.feed(text)
                _stream.play()  # Bloqueante: aguarda a fala terminar
        except Exception as e:
            print(f"\n[TTS Error] Falha na síntese de voz: {e}")
            traceback.print_exc()
        finally:
            _tts_queue.task_done()

def init_tts():
    """Puxa instâncias do RealtimeTTS apenas se habilitado."""
    global _engine, _stream, _worker_thread
    if not TTS_ENABLED:
        return

    if not AZURE_SPEECH_KEY or not AZURE_SPEECH_REGION:
        print("\n⚠️  [TTS] Chaves da Azure não encontradas. TTS desabilitado.")
        return

    try:
        from RealtimeTTS import TextToAudioStream, AzureEngine
        
        # Inicializa o motor
        _engine = AzureEngine(
            speech_key=AZURE_SPEECH_KEY, 
            service_region=AZURE_SPEECH_REGION,
            voice=AZURE_SPEECH_VOICE
        )
        _stream = TextToAudioStream(_engine)
        
        # Inicia a thread worker que garante a fila linear
        _worker_thread = threading.Thread(target=_tts_worker, daemon=True)
        _worker_thread.start()
        
    except ImportError as e:
        print(f"\n⚠️  [TTS] Erro de dependência ao carregar RealtimeTTS: {e}\n(Rode: pip install RealtimeTTS azure-cognitiveservices-speech audioop-lts)")
    except Exception as e:
        print(f"\n⚠️  [TTS] Falha ao iniciar: {e}")

def speak(text: str) -> None:
    """
    Sintetiza texto em fala. Enfileira o texto se já estiver falando.
    
    Args:
        text: Texto para sintetizar.
    """
    if not TTS_ENABLED or not _stream or not _worker_thread:
        return
        
    # Colocamos na fila, a thread background cuida do resto
    _tts_queue.put(text)

def stop_tts() -> None:
    """Para a fala atual imediatamente e limpa a fila."""
    if not TTS_ENABLED or not _stream:
        return
        
    # Esvazia a fila
    while not _tts_queue.empty():
        try:
            _tts_queue.get_nowait()
            _tts_queue.task_done()
        except queue.Empty:
            break
            
    # Para a fala se estiver rolando
    try:
        if _stream.is_playing():
            _stream.stop()
    except AttributeError:
        # Em algumas versões o método pode mudar, tenta garantir proteção
        pass
