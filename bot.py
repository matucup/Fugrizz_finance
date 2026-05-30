import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

TOKEN = os.environ.get("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Kirim transaksi dengan format:\n"
        "keterangan nominal\n\n"
        "Contoh: makan siang 35000"
    )

async def catat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pesan = update.message.text.strip()
    match = re.match(r"^(.+?)\s+(\d+)$", pesan)
    if match:
        keterangan = match.group(1).strip().title()
        nominal = int(match.group(2))
        nominal_fmt = f"Rp{nominal:,}".replace(",", ".")
        await update.message.reply_text(
            f"Dicatat!\n"
            f"- {keterangan}\n"
            f"- {nominal_fmt}"
        )
    else:
        await update.message.reply_text(
            "Format tidak dikenali.\n"
            "Contoh yang benar: makan siang 35000"
        )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, catat))
app.run_polling()
