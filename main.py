"""
main.py — Ponto de entrada da Aiko.

Loop principal do terminal: lê entrada do usuário, processa, exibe resposta.
Suporta modo voz contínuo via /voz_continuo.
"""

import sys
from core.orchestrator import Orchestrator
from config.settings import PERSONA_NAME
from voice.tts import init_tts, stop_tts
from voice.stt import get_voice_input
from voice.stt import (
    start_continuous_voice,
    stop_continuous_voice,
    wait_for_next_speech,
    signal_ready_for_next,
)

# Inicializa o modelo dinamicamente dentro dos modulos que precisam
BANNER = f"""
╔══════════════════════════════════════════╗
║          {PERSONA_NAME} — Assistente Virtual          ║
║                                          ║
║  Digite sua mensagem corporativa.        ║
║  Ex: "abre o chrome"  |  "oi, tudo bem" ║
║  Para falar: digite "/voz"              ║
║  Para voz contínua: "/voz_continuo"     ║
║  Para sair: Ctrl+C ou "sair"             ║
╚══════════════════════════════════════════╝
"""


def main() -> None:
    """Loop principal de interação via terminal."""

    print(BANNER)
    init_tts()

    # Verifica se o Ollama está acessível

    from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL
    try:
        import urllib.request
        urllib.request.urlopen(OLLAMA_BASE_URL, timeout=2)
    except Exception:
        print(
            f"⚠️  ATENÇÃO: Ollama não encontrado em {OLLAMA_BASE_URL}\n"
            f"   1. Instale em: https://ollama.com/download\n"
            f"   2. Rode no terminal: ollama serve\n"
            f"   3. Baixe o modelo:   ollama pull {OLLAMA_MODEL}\n"
        )

    orchestrator = Orchestrator()

    while True:
        try:
            # Lê input — o prompt visual indica que é sua vez de falar
            user_input = input("Você › ").strip()

            # Comando de saída
            if user_input.lower() in ("sair", "exit", "quit", "tchau"):
                print(f"[{PERSONA_NAME}] Até mais. Qualquer coisa, me chama.")
                stop_tts()
                sys.exit(0)

            # Comando de voz pontual
            if user_input.lower() == "/voz":
                transcribed_text = get_voice_input()

                if not transcribed_text:
                    print("⚠️  [Voz] Não consegui entender o áudio.")
                    continue

                print(f"Você (Voz) › {transcribed_text}")
                user_input = transcribed_text
                # Agora o fluxo segue normalmente como se tivesse sido digitado

            # Comando de voz contínua
            if user_input.lower() in ("/voz_continuo", "/continuo"):
                _run_continuous_voice(orchestrator)
                continue

            # Ignora entradas vazias
            if not user_input:
                continue

            # Processa e exibe a resposta
            response = orchestrator.handle(user_input)
            if response:
                print(f"{response}\n")

        except KeyboardInterrupt:
            # Ctrl+C sai com elegância
            print(f"\n[{PERSONA_NAME}] Ok, ido embora. Tchau.")
            stop_tts()
            sys.exit(0)

        except EOFError:
            # Pipe de stdin fechado
            sys.exit(0)


def _run_continuous_voice(orchestrator: Orchestrator) -> None:
    """
    Executa o loop de voz contínua.

    Fluxo:
      1. Ativa o microfone em modo contínuo
      2. Aguarda a fala do usuário (VAD detecta o fim)
      3. Processa através do Orchestrator
      4. Sinaliza que está pronto para a próxima fala
      5. Se o usuário disser "sair", encerra o modo contínuo
    """
    from core.orchestrator import detect_intent
    from core.brain import generate_response
    from actions.executor import execute
    from voice.tts import speak
    from config.settings import PERSONA_NAME

    start_continuous_voice()

    try:
        while True:
            transcribed_text = wait_for_next_speech()

            if not transcribed_text:
                print("[Voz] Áudio vazio, continuando...")
                signal_ready_for_next()
                continue

            print(f"\nVocê › {transcribed_text}")

            # Permite sair do modo contínuo
            if transcribed_text.lower() in ("sair", "exit", "tchau", "parar", "suficiente"):
                print(f"[{PERSONA_NAME}] Voltando ao modo texto. Qualquer coisa, me chama.")
                break

            # Ignora entradas vazias
            if not transcribed_text:
                signal_ready_for_next()
                continue

            # Processa normalmente
            response = orchestrator.handle(transcribed_text)
            if response:
                print(f"{response}\n")

            # Sinaliza que o sistema está pronto para a próxima fala
            signal_ready_for_next()

    finally:
        stop_continuous_voice()


if __name__ == "__main__":
    main()
