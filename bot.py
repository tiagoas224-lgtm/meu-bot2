import random
import asyncio
import time
from collections import defaultdict

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# 🔐 CONFIG
TOKEN = "8545874935:AAFcGqW7RO-ZWF3yXTZ6A3OBfdastAmHyHA"
ADM_ID = 7837577709
PIX_CHAVE = "6e82ec28-b0a3-4e80-891e-7056fb9f5fac"

# 📊 DADOS
participantes = []
pontos = {}
historico = []
cofre = 0.0

# 🛡️ ANTI-SPAM
cooldown = 3
ultimo_click = defaultdict(float)

def anti_spam(user_id):
    agora = time.time()
    if agora - ultimo_click[user_id] < cooldown:
        return False
    ultimo_click[user_id] = agora
    return True

# 🎰 MENU PRINCIPAL
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    teclado = [
        [InlineKeyboardButton("🎰 ENTRAR", callback_data="entrar")],
        [InlineKeyboardButton("📊 RANKING", callback_data="ranking")],
        [InlineKeyboardButton("💰 COFRE", callback_data="cofre")],
        [InlineKeyboardButton("🏆 VENCEDOR", callback_data="vencedor")],
        [InlineKeyboardButton("🎲 ROLETA", callback_data="roleta")]
    ]

    await update.message.reply_text(
        "🎰 CASINO AO VIVO 🔥",
        reply_markup=InlineKeyboardMarkup(teclado)
    )

# 📊 RANKING
def ranking():
    ordenado = sorted(pontos.items(), key=lambda x: x[1], reverse=True)

    texto = "🏆 RANKING AO VIVO 🏆\n\n"

    for i, (u, p) in enumerate(ordenado[:10]):
        texto += f"{i+1}º @{u} - {p} pts 💰\n"

    return texto

# 🎮 ENTRADA
def entrar_jogo(username, valor):
    global cofre

    participantes.append(username)
    pontos[username] = pontos.get(username, 0) + valor
    cofre += valor

# 💬 BOTÕES
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    user = q.from_user
    user_id = user.id
    username = user.username or user.first_name

    # 🛡️ ANTI-SPAM
    if not anti_spam(user_id):
        await q.answer("⏳ Aguarde...", show_alert=True)
        return

    # 🎰 MENU ENTRAR
    if q.data == "entrar":

        teclado = [
            [InlineKeyboardButton("💵 R$1", callback_data="p1"),
             InlineKeyboardButton("💵 R$5", callback_data="p5")],
            [InlineKeyboardButton("💵 R$10", callback_data="p10")]
        ]

        await q.message.edit_text(
            "💰 ESCOLHA O VALOR",
            reply_markup=InlineKeyboardMarkup(teclado)
        )

    # 📊 RANKING
    elif q.data == "ranking":
        await q.message.edit_text(ranking())

    # 💰 COFRE
    elif q.data == "cofre":
        await q.message.edit_text(f"💰 Cofre atual: R${cofre:.2f}")

    # 🏆 VENCEDOR
    elif q.data == "vencedor":
        ultimo = historico[-1] if historico else "nenhum"
        await q.message.edit_text(f"🏆 Último vencedor: @{ultimo}")

    # 🎲 ROLETA
    elif q.data == "roleta":

        msg = await q.message.edit_text("🎲 Girando roleta...")

        if not participantes:
            await msg.edit_text("❌ Nenhum jogador ainda")
            return

        for _ in range(8):
            await msg.edit_text(f"🎰 {random.choice(participantes)}")
            await asyncio.sleep(0.3)

        vencedor = random.choice(participantes)
        historico.append(vencedor)

        await msg.edit_text(f"""
🏆 RESULTADO FINAL

👑 @{vencedor}
🎉 VENCEDOR DA RODADA
""")

    # 💵 PLANOS
    elif q.data.startswith("p"):

        valor = int(q.data.replace("p", ""))

        await context.bot.send_message(
            chat_id=user_id,
            text=f"""
💰 PAGAMENTO PIX

🔑 {PIX_CHAVE}

💵 Valor: R${valor}

📸 Envie comprovante aqui
"""
        )

        entrar_jogo(username, valor)

# 🚀 BOT START
app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))

print("🎰 CASINO BOT ONLINE")
app.run_polling()