import os

import httpx
from dotenv import load_dotenv
from telegram import (
    Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, ConversationHandler, filters
)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise SystemExit("Defina TELEGRAM_TOKEN no arquivo .env")

API = "https://pokeapi.co/api/v2"
ESPERANDO_NOME = 1

NOMES_STATS = {
    "hp": "HP",
    "attack": "Ataque",
    "defense": "Defesa",
    "special-attack": "Atq. Esp.",
    "special-defense": "Def. Esp.",
    "speed": "Velocidade",
}


async def get_json(url: str):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        return r.json() if r.status_code == 200 else None


async def buscar_pokemon(nome: str):
    """Busca pelo nome ou número. Se falhar, tenta pela espécie (ex: wormadam)."""
    dados = await get_json(f"{API}/pokemon/{nome}")
    if dados:
        return dados
    especie = await get_json(f"{API}/pokemon-species/{nome}")
    if especie:
        padrao = next(v for v in especie["varieties"] if v["is_default"])
        return await get_json(padrao["pokemon"]["url"])
    return None


def teclado(nome: str, shiny: bool) -> InlineKeyboardMarkup:
    botao_forma = (
        InlineKeyboardButton("🔙 Versão normal", callback_data=f"normal:{nome}")
        if shiny
        else InlineKeyboardButton("✨ Ver shiny", callback_data=f"shiny:{nome}")
    )
    botao_evo = InlineKeyboardButton("🔄 Evoluções", callback_data=f"evo:{nome}")
    return InlineKeyboardMarkup([[botao_forma, botao_evo]])


async def montar_card(nome: str, shiny: bool = False):
    dados = await buscar_pokemon(nome)
    if not dados:
        return None

    especie = await get_json(dados["species"]["url"])

    tipos = ", ".join(t["type"]["name"].capitalize() for t in dados["types"])
    habilidades = ", ".join(
        h["ability"]["name"].replace("-", " ").title() + (" (oculta)" if h["is_hidden"] else "")
        for h in dados["abilities"]
    )
    geracao = especie["generation"]["name"].split("-")[1].upper()
    stats = "\n".join(
        f"• {NOMES_STATS.get(s['stat']['name'], s['stat']['name'])}: {s['base_stat']}"
        for s in dados["stats"]
    )
    total = sum(s["base_stat"] for s in dados["stats"])

    legenda = (
        f"<b>{dados['name'].replace('-', ' ').title()}</b> — #{especie['id']}"
        f"{' ✨' if shiny else ''}\n"
        f"Tipo: {tipos}\n"
        f"Geração: {geracao}\n"
        f"Altura: {dados['height'] / 10} m | Peso: {dados['weight'] / 10} kg\n"
        f"Habilidades: {habilidades}\n\n"
        f"<b>Stats</b> (total {total})\n{stats}"
    )

    artwork = dados["sprites"]["other"]["official-artwork"]
    sprites = dados["sprites"]
    if shiny:
        imagem = artwork["front_shiny"] or sprites["front_shiny"]
    else:
        imagem = artwork["front_default"] or sprites["front_default"]

    return dados["name"], imagem, legenda


def caminhos_evolucao(no, prefixo=()):
    atual = prefixo + (no["species"]["name"],)
    if not no["evolves_to"]:
        return [atual]
    resultado = []
    for proximo in no["evolves_to"]:
        resultado += caminhos_evolucao(proximo, atual)
    return resultado


TEXTO_AJUDA = (
    "<b>📖 Ajuda do Pokédex Bot</b>\n\n"
    "<b>Comandos</b>\n"
    "/pokemon — pesquisar um pokemon\n"
    "/cancelar — cancelar a pesquisa em andamento\n"
    "/help — mostrar esta mensagem\n\n"
    "<b>Como pesquisar</b>\n"
    "Envie /pokemon e depois o nome (ex: <code>pikachu</code>) "
    "ou o número da Pokédex (ex: <code>25</code>).\n\n"
    "<b>O que você recebe</b>\n"
    "• Imagem, nome e número da Pokédex\n"
    "• Tipos, geração, altura e peso\n"
    "• Habilidades e stats\n\n"
    "<b>Botões</b>\n"
    "✨ Ver shiny — mostra a versão shiny (e volta para a normal)\n"
    "🔄 Evoluções — mostra a linha evolutiva e deixa abrir cada pokemon"
)


async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEXTO_AJUDA, parse_mode="HTML")


async def boas_vindas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! Eu sou um bot de Pokédex. 👋\n\n" + TEXTO_AJUDA, parse_mode="HTML"
    )


async def definir_menu(app):
    """Faz os comandos aparecerem no menu do Telegram (botão 'Menu' no chat)."""
    await app.bot.set_my_commands([
        BotCommand("pokemon", "Pesquisar um pokemon"),
        BotCommand("cancelar", "Cancelar a pesquisa"),
        BotCommand("help", "Ver todos os comandos"),
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Qual pokemon deseja saber sobre? (nome ou número)")
    return ESPERANDO_NOME


async def receber_nome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip().lower().replace(" ", "-")
    card = await montar_card(texto)
    if not card:
        await update.message.reply_text("Não encontrei esse pokemon. Tenta outro nome!")
        return ESPERANDO_NOME

    nome, imagem, legenda = card
    await update.message.reply_photo(
        photo=imagem, caption=legenda, parse_mode="HTML",
        reply_markup=teclado(nome, shiny=False),
    )
    return ConversationHandler.END


async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    acao, nome = query.data.split(":", 1)

    if acao in ("shiny", "normal"):
        shiny = acao == "shiny"
        card = await montar_card(nome, shiny=shiny)
        if not card:
            return
        nome, imagem, legenda = card
        await query.edit_message_media(
            media=InputMediaPhoto(media=imagem, caption=legenda, parse_mode="HTML"),
            reply_markup=teclado(nome, shiny),
        )

    elif acao == "evo":
        dados = await buscar_pokemon(nome)
        especie = await get_json(dados["species"]["url"])
        cadeia = await get_json(especie["evolution_chain"]["url"])
        caminhos = caminhos_evolucao(cadeia["chain"])

        if len(caminhos) == 1 and len(caminhos[0]) == 1:
            await query.message.reply_text(f"{nome.title()} não possui evoluções.")
            return

        texto = "<b>Linha evolutiva</b>\n" + "\n".join(
            " → ".join(n.replace("-", " ").title() for n in c) for c in caminhos
        )

        # um botão para cada pokemon da cadeia, 3 por linha
        unicos = list(dict.fromkeys(n for c in caminhos for n in c))
        botoes_ver = [
            InlineKeyboardButton(n.replace("-", " ").title(), callback_data=f"ver:{n}")
            for n in unicos
        ]
        linhas = [botoes_ver[i:i + 3] for i in range(0, len(botoes_ver), 3)]
        await query.message.reply_text(
            texto, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(linhas)
        )

    elif acao == "ver":
        card = await montar_card(nome)
        if not card:
            await query.message.reply_text("Não consegui carregar esse pokemon.")
            return
        nome, imagem, legenda = card
        await query.message.reply_photo(
            photo=imagem, caption=legenda, parse_mode="HTML",
            reply_markup=teclado(nome, shiny=False),
        )


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelado.")
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(TOKEN).post_init(definir_menu).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("pokemon", start)],
        states={
            ESPERANDO_NOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_nome)]
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )
    app.add_handler(conv)
    app.add_handler(CommandHandler("start", boas_vindas))
    app.add_handler(CommandHandler(["help", "ajuda"], ajuda))
    app.add_handler(CallbackQueryHandler(botoes))
    app.run_polling()


if __name__ == "__main__":
    main()
