# AI:Daughter — Saphira

Assistente de desktop com IA local para Windows. Converse por texto ou voz, peça para abrir programas e peça para "olhar" a tela. Tudo roda na sua máquina — sem API key para o LLM.

## Funcionalidades

- **Chat local** — LLM via [Ollama](https://ollama.com) com modelo `gemma3:4b`, zero custo
- **Voz (STT)** — Speech-to-Text com [RealtimeSTT](https://github.com/KoljaB/RealtimeSTT) + Whisper, detecção de voz automática (VAD)
- **Fala (TTS)** — Text-to-Speech via [RealtimeTTS](https://github.com/KoljaB/RealtimeTTS) + Azure Speech
- **Visão de tela** — Captura e análise do que está na tela com [Moondream](https://github.com/vikhyat/moondream)
- **Controle do computador** — Abre aplicativos por comando de voz/texto, com busca dinâmica de executáveis e sistema de apelidos
- **Memória de sessão** — Histórico de conversa mantido em contexto

## Arquitetura

```
Ai-daughter/
├── main.py              # Ponto de entrada, loop principal
├── Modelfile            # Persona "Saphira" embutida no modelo Ollama
│
├── core/
│   ├── orchestrator.py  # Detecta intenção e coordena os módulos
│   ├── brain.py         # Comunicação com o Ollama (LLM), spinner de loading
│   └── memory.py        # Memória de conversa da sessão (rolling window)
│
├── voice/
│   ├── stt.py           # Speech-to-Text via RealtimeSTT + Whisper
│   └── tts.py           # Text-to-Speech via RealtimeTTS + Azure
│
├── actions/
│   ├── commands.py      # Mapeamento de comandos e apelidos de apps
│   ├── executor.py      # Executa ações (abre apps) via subprocess
│   ├── finder.py        # Busca dinâmica de .exe no sistema de arquivos
│   └── vision.py        # Captura de tela + análise com Moondream
│
└── config/
    ├── settings.py      # Configurações centrais (env, paths, keywords)
    ├── responses.json   # Respostas predefinidas do sistema
    └── responses.py     # Loader de respostas com formatação
```

## Requisitos

- **Python 3.12+**
- **[Ollama](https://ollama.com/download)** rodando localmente
- **Windows 10/11** (busca de apps, captura de tela)

## Instalação

### 1. Clone e dependências

```bash
cd Ai-daughter
pip install -r requirements.txt
```

### 2. Ollama + Modelo

Baixe o modelo base:

```bash
ollama pull gemma3:4b
ollama pull moondream
```

Crie o modelo customizado com a persona da Saphira (opcional, mas recomendado):

```bash
ollama create ai:daughter -f Modelfile
```

### 3. Configuração

Copie o arquivo de exemplo e edite:

```bash
cp .env.example .env
```

Configure as variáveis no `.env`:

| Variável | Descrição | Padrão |
|---|---|---|
| `OLLAMA_BASE_URL` | URL do servidor Ollama | `http://localhost:11434` |
| `OLLAMA_MODEL` | Modelo LLM | `ai:daughter` |
| `OLLAMA_VISION_MODEL` | Modelo de visão | `moondream` |
| `WHISPER_MODEL` | Modelo Whisper para STT | `small` |
| `TTS_ENABLED` | Habilitar fala | `False` |
| `AZURE_SPEECH_KEY` | Chave Azure Speech | — |
| `AZURE_SPEECH_REGION` | Região Azure | `brazilsouth` |
| `AZURE_SPEECH_VOICE` | Voz Azure | `pt-BR-ThalitaNeural` |
| `MAX_TURNS` | Pares de mensagem em memória | `5` |

## Uso

```bash
python main.py
```

### Modos de interação

| Entrada | Ação |
|---|---|
| `"oi, tudo bem?"` | Chat normal com a IA |
| `"abre o chrome"` | Abre o Google Chrome |
| `"/voz"` | Ativa captura de microfone (fale naturalmente, VAD detecta o fim) |
| `"/voz_continuo"` | Modo voz contínuo — o microfone reativa automaticamente após cada resposta, permitindo conversa fluida. Diga "sair" para encerrar. |
| `"olha minha tela"` | Captura a tela e analisa com Moondream |
| `"limpar"` | Limpa a memória da sessão |
| `"sair"` / `Ctrl+C` | Encerra o programa |

### Comandos e apelidos

O sistema reconhece comandos como "abra", "abre", "abrir", "open", "executar", "roda", etc. Aplicativos pré-cadastrados incluem Chrome, VS Code, Bloco de Notas, Explorador. Apelidos configuráveis no `config/commands.py` (ex: "navegador" → zen, "jogos" → steam).

### Adicionando novos apps

- **Registrado:** adicione o caminho em `APP_PATHS` no `settings.py` e o comando no `COMMAND_MAP` em `commands.py`
- **Dinâmico:** peças como "abra o spotify" buscam o `.exe automaticamente no disco

## Persona

A Saphira tem uma personalidade sarcástica, direta, com humor seco. A persona é definida no `Modelfile` e embutida no modelo customizado, ou como fallback no `SYSTEM_PROMPT` em `settings.py`.

## Notas

- O TTS requer credenciais da Azure Speech — sem elas, o sistema funciona normalmente sem fala
- A visão de tela é limitada pelo hardware, pois o modelo Moondream roda localmente na CPU
- STT com `compute_type=int8` para performance em CPU
