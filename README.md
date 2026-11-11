# 🔎 Pokédex Bot para Telegram

Bot de Telegram que mostra informações de qualquer pokemon. Basta enviar o nome ou o número da Pokédex e ele responde com a imagem, os dados e botões interativos.

Os dados vêm da [PokéAPI](https://pokeapi.co), que é gratuita e não exige chave de acesso.

## ✨ Funcionalidades

- Pesquisa por **nome** (`pikachu`) ou **número da Pokédex** (`25`)
- Mostra imagem oficial, nome, número, tipos, geração, altura e peso
- Lista as habilidades (indicando quais são ocultas) e os stats base com o total
- Botão **✨ Ver shiny** para alternar entre a versão normal e a shiny
- Botão **🔄 Evoluções** para ver a linha evolutiva e abrir qualquer pokemon da cadeia
- Comando `/help` com a lista de interações
- Menu de comandos registrado automaticamente no Telegram

## 📋 Requisitos

- Python 3.9 ou superior
- Uma conta no Telegram
- Um token de bot, criado com o [@BotFather](https://t.me/BotFather)

## 🚀 Instalação

1. Clone ou baixe o projeto e entre na pasta:

   ```bash
   cd pokemon-bot
   ```

2. (Opcional, mas recomendado) Crie um ambiente virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate      # Linux/macOS
   venv\Scripts\activate         # Windows
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

## 🔑 Configuração do token

1. No Telegram, fale com o **@BotFather**, envie `/newbot` e siga as instruções. Ele vai te entregar um token.
2. Crie um arquivo chamado `.env` na mesma pasta do `pokemon_bot.py`:

   ```
   TELEGRAM_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
   ```

   Use o seu token real, sem aspas e sem espaços em volta do `=`.

> ⚠️ **Nunca compartilhe o token nem suba o arquivo `.env` para o GitHub.** Adicione `.env` ao seu `.gitignore`. Se o token vazar, gere um novo com `/revoke` no @BotFather.

## ▶️ Como rodar

```bash
python pokemon_bot.py
```

Deixe o terminal aberto. Enquanto o programa estiver rodando, o bot responde no Telegram.

## 💬 Comandos

| Comando     | O que faz                                      |
|-------------|------------------------------------------------|
| `/start`    | Mensagem de boas-vindas com a ajuda            |
| `/pokemon`  | Inicia uma pesquisa (o bot pergunta o nome)    |
| `/cancelar` | Cancela a pesquisa em andamento                |
| `/help`     | Mostra todas as interações disponíveis         |

### Exemplo de uso

```
Você: /pokemon
Bot:  Qual pokemon deseja saber sobre? (nome ou número)
Você: pikachu
Bot:  [imagem + dados + botões ✨ Ver shiny | 🔄 Evoluções]
```

## 🧠 Como funciona

1. O `/pokemon` inicia uma conversa (`ConversationHandler`) e o bot espera o nome.
2. O bot consulta a PokéAPI: uma chamada em `/pokemon` (dados gerais, imagens, stats) e outra em `/pokemon-species` (geração e cadeia evolutiva).
3. A resposta é enviada como foto com legenda em HTML e botões inline.
4. Cada botão carrega um texto no formato `acao:nome` (ex: `shiny:pikachu`), que o `CallbackQueryHandler` usa para decidir o que fazer.
5. A linha evolutiva é uma árvore na API, percorrida de forma recursiva para listar todos os caminhos possíveis (incluindo ramificações, como a do Eevee).

## 📁 Estrutura do projeto

```
pokemon-bot/
├── pokemon_bot.py     # código do bot
├── requirements.txt   # dependências
├── .env               # token do bot (não versionar)
└── README.md
```

## 🛠️ Tecnologias

- [Python](https://www.python.org/)
- [python-telegram-bot](https://python-telegram-bot.org/) — integração com o Telegram
- [httpx](https://www.python-httpx.org/) — requisições assíncronas
- [python-dotenv](https://pypi.org/project/python-dotenv/) — leitura do `.env`
- [PokéAPI](https://pokeapi.co) — fonte dos dados


## 📄 Créditos

Dados e imagens fornecidos pela [PokéAPI](https://pokeapi.co). Pokémon e seus nomes são marcas registradas da Nintendo, Game Freak e The Pokémon Company. Este é um projeto de estudo, sem fins comerciais.
