"""
settings.py — Configurações centrais do projeto.

Todas as variáveis de ambiente e constantes ficam aqui.
Assim, nenhum outro arquivo precisa saber de onde vêm as configs.
"""

import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env (se existir)
load_dotenv()

# ─── Ollama (LLM local, gratuito) ─────────────────────────────────────────────
# Ollama roda um servidor local em http://localhost:11434
# Não precisa de API key — é tudo na sua máquina.
#
# Modelo customizado AI:Daughter:
#   A persona da Saphira está embutida diretamente no modelo.
#   Para criá-lo, rode no terminal:
#     ollama create ai:daughter -f Modelfile
#
# Fallback (modelo base sem persona embutida):
#   Defina OLLAMA_MODEL=gemma3:4b no .env para usar sem o Modelfile.
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "ai:daughter")
OLLAMA_VISION_MODEL: str = os.getenv("OLLAMA_VISION_MODEL", "moondream")

# ─── Voz (STT e TTS) ──────────────────────────────────────────────────────────
WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "small")
STT_RATE: int = int(os.getenv("STT_RATE", "16000"))  # Sample rate padrão p/ Whisper

# TTS (Sintetizador de voz via Azure e RealtimeTTS)
TTS_ENABLED: bool = os.getenv("TTS_ENABLED", "False").lower() in ("true", "1", "yes")
AZURE_SPEECH_KEY: str | None = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION: str | None = os.getenv("AZURE_SPEECH_REGION")
AZURE_SPEECH_VOICE: str = os.getenv("AZURE_SPEECH_VOICE", "pt-BR-ThalitaNeural")

# ─── Memória de conversa ──────────────────────────────────────────────────────
# Quantos pares (usuário + assistente) são mantidos no histórico enviado ao
# modelo. Valores menores = contexto menor = 1º token mais rápido.
# Ajuste via MAX_TURNS no .env (padrão: 5).
MAX_TURNS: int = int(os.getenv("MAX_TURNS", "5"))

# ─── Persona ──────────────────────────────────────────────────────────────────
PERSONA_NAME: str = "Saphira"

# SYSTEM_PROMPT é usado apenas como fallback quando o modelo 'ai:daughter'
# não está disponível (ex: usando gemma3:4b diretamente).
# Quando usar 'ai:daughter', a persona já está embutida no Modelfile.
SYSTEM_PROMPT: str = f"""
Você é {PERSONA_NAME}, uma assistente pessoal extremamente inteligente e discreta.

Sua personalidade:
- Levemente sarcástica, mas sempre útil
- Respostas curtas e diretas — nada de enrolação
- Tom descontraído e amigável
- Nunca menciona que é uma IA, modelo ou programa
- Se alguém perguntar quem você é, diga apenas que é {PERSONA_NAME}
- Fala em português do Brasil

Exemplos do seu estilo:
- "Feito. Qualquer coisa, me chama."
- "Interessante. Você tem certeza disso?"
- "Tá bom, mas da próxima pensa melhor antes de me perguntar."
"""

# Flag que indica se o modelo customizado tem a persona embutida
# Se True, o SYSTEM_PROMPT não é enviado nas mensagens (evita duplicação)
USE_BUILTIN_PERSONA: bool = OLLAMA_MODEL == "ai:daughter"

# ─── Comandos suportados ──────────────────────────────────────────────────────
# Palavras-chave que disparam detecção de intenção como "command"
COMMAND_KEYWORDS: list[str] = [
    "abrir", "abra", "abre", "abrir o", "open",
    "fechar", "feche", "fecha",
    "executar", "execute", "roda",
    "iniciar", "inicia",
    "ligar", "liga",
]

# Palavras-chave que disparam a deteção de visão
VISION_KEYWORDS: list[str] = [
    "veja", "olha", "olhar", "olhe", "minha tela", "na tela"
]

# ─── Caminhos de aplicativos ──────────────────────────────────────────────────
# Mapeamento de nome → caminho do executável no Windows
APP_PATHS: dict[str, str] = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "vscode": r"C:\Users\{username}\AppData\Local\Programs\Microsoft VS Code\Code.exe".format(
        username=os.getenv("USERNAME", "User")
    ),
    "notepad": "notepad.exe",
    "explorer": "explorer.exe",
}
