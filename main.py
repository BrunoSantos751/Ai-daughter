"""
main.py — Ponto de entrada da Aiko.

Loop principal do terminal: lê entrada do usuário, processa, exibe resposta.
"""

import sys
from core.orchestrator import Orchestrator
from config.settings import PERSONA_NAME
from voice.tts import init_tts, stop_tts

# Inicializa o modelo dinamicamente dentro dos modulos que precisam
BANNER = f"""
╔══════════════════════════════════════════╗
║          {PERSONA_NAME} — Assistente Virtual          ║
║                                          ║
║  Digite sua mensagem corporativa.        ║
║  Ex: "abre o chrome"  |  "oi, tudo bem" ║
║  Para falar: digite "/voz"              ║
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

            # Invocação do módulo de voz
            if user_input.lower() == "/voz":
                from voice.stt import get_voice_input
                
                transcribed_text = get_voice_input()
                
                if not transcribed_text:
                    print("⚠️  [Voz] Não consegui entender o áudio.")
                    continue
                
                print(f"Você (Voz) › {transcribed_text}")
                user_input = transcribed_text
                # Agora o fluxo segue normalmente como se tivesse sido digitado

            # Ignora entradas vazias
            if not user_input:
                continue

            # Processa e exibe a resposta
            response = orchestrator.handle(user_input)
            if response:
                print(f"{response}\n")

        except KeyboardInterrupt:
            # Ctrl+C sai com elegância
            print(f"\n[{PERSONA_NAME}] Ok, indo embora. Tchau.")
            stop_tts()
            sys.exit(0)

        except EOFError:
            # Pipe de stdin fechado
            sys.exit(0)


if __name__ == "__main__":
    main()
