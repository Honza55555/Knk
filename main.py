import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)

# načtení proměnných z env
BOT_TOKEN = os.environ["BOT_TOKEN"]
BASE_URL  = os.environ["BASE_URL"]    # např. https://your-service.onrender.com
PORT      = int(os.environ.get("PORT", 5000))

# Flask instance
app = Flask(__name__)

# Telegram bot app
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# --- HANDLERY ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🇨🇿 Čeština", callback_data="lang_cs"),
            InlineKeyboardButton("🌍 English", callback_data="lang_en"),
        ]
    ]
    await update.message.reply_text(
        "☕️ Welcome to Coffee Perk!\n"
        "We’re happy to see you here. 🌟\n"
        "Please choose your language. 🗣️",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def lang_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.callback_query.data
    await update.callback_query.answer()

    if code == "lang_cs":
        prompt = "Na co se mě můžeš zeptat:"
        opts = [
            ("menu_cs",    "🧾 Menu a nabídka"),
            ("hours_cs",   "🕐 Otevírací doba"),
            ("where_cs",   "📍 Kde nás najdete"),
            ("contact_cs", "📞 Kontakt / Rezervace"),
            ("preorder_cs","📦 Předobjednávka"),
            ("why_cs",     "😎 Proč k nám?"),
        ]
    else:
        prompt = "What can you ask me:"
        opts = [
            ("menu_en",    "🧾 Menu & Offer"),
            ("hours_en",   "🕐 Opening Hours"),
            ("where_en",   "📍 Location"),
            ("contact_en", "📞 Contact / Booking"),
            ("preorder_en","📦 Pre-order"),
            ("why_en",     "😎 Why Visit"),
        ]

    keyboard = [[InlineKeyboardButton(label, callback_data=data)] for data,label in opts]
    await update.callback_query.edit_message_text(prompt, reply_markup=InlineKeyboardMarkup(keyboard))

SECTIONS = {
    # Czech
    "menu_cs":    "🥐 **COFFEE PERK MENU** ☕️\n\n☕ Výběrová káva\n🍳 Snídaně…",
    "hours_cs":   "🕐 **KDY MÁME OTEVŘENO?**\n\n📅 Po–Pá: 7:30–17:00\n…",
    "where_cs":   "📍 **KDE NÁS NAJDETE?**\n\n🏠 Vyskočilova…",
    "contact_cs": "📞 **KONTAKTUJTE NÁS**\n\n📬 info@coffeeperk.cz\n…",
    "preorder_cs":"📦 **PŘEDOBJEDNÁVKY**\n\nBrzy spustíme…",
    "why_cs":     "😎 **DŮVODY, PROČ SI ZAJÍT NA KÁVU**\n\n☕ Protože…",

    # English
    "menu_en":    "🥐 **COFFEE PERK MENU** ☕️\n\n☕ Specialty coffee\n…",
    "hours_en":   "🕐 **OPENING HOURS**\n\n📅 Mon–Fri: 7:30 AM – 5 PM\n…",
    "where_en":   "📍 **LOCATION**\n\n🏠 Vyskočilova…",
    "contact_en": "📞 **CONTACT / BOOKING**\n\n📬 info@coffeeperk.cz\n…",
    "preorder_en":"📦 **PRE-ORDER**\n\nComing soon…",
    "why_en":     "😎 **WHY VISIT US?**\n\n☕ Because life’s better…",
}

async def show_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = update.callback_query.data
    await update.callback_query.answer()
    text = SECTIONS.get(key, "❌ Sekce nenalezena.")
    await update.callback_query.edit_message_text(text, parse_mode="Markdown")

# registrace handlerů
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(lang_select, pattern="^lang_"))
bot_app.add_handler(CallbackQueryHandler(show_section, pattern="^(menu|hours|where|contact|preorder|why)_"))

# webhook endpoint
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot_app.bot)
    bot_app._handle_update(update)
    return "OK"

if __name__ == "__main__":
    bot_app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        # cesta, na které Telegram pošle POSTy
        url_path=BOT_TOKEN,
        # vlastní webhook URL, kam Telegram webhook nastaví
        webhook_url=f"{BASE_URL}/{BOT_TOKEN}",
        # zahodí nevyřízené updety při startu
        drop_pending_updates=True,
    )
