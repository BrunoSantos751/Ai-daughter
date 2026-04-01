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
# Modelos recomendados (escolha um de acordo com sua RAM):
#   gemma3:4b   → ~4 GB RAM  (rápido, ótima qualidade)
#   llama3.2:3b → ~3 GB RAM  (menor, bom para hardware limitado)
#   mistral     → ~5 GB RAM  (muito bom para seguir instruções)
#   phi4-mini   → ~2.5 GB RAM (ultraleve)
#
# Para baixar o modelo escolhido, rode no terminal:
#   ollama pull gemma3:4b
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "gemma3:4b")

# ─── Persona ──────────────────────────────────────────────────────────────────
PERSONA_NAME: str = "Saphira"

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

# ─── Comandos suportados ──────────────────────────────────────────────────────
# Palavras-chave que disparam detecção de intenção como "command"
COMMAND_KEYWORDS: list[str] = [
    "abrir", "abra", "abre", "abrir o", "open",
    "fechar", "feche", "fecha",
    "executar", "execute", "roda",
    "iniciar", "inicia",
    "ligar", "liga",
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
