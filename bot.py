import os
import re
import json
import gspread
from google.oauth2.service_account import Credentials
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from datetime import datetime

TOKEN = os.environ.get("TOKEN")
SHEET_ID = os.environ.get("SHEET_ID")
GOOGLE_CREDS = os.environ.get("GOOGLE_CREDS")

def get_sheet():
    creds_dict = json.loads(GOOGLE_CREDS)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).sheet1

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
        tanggal = datetime.now().strftime("%d/%m/%Y %H:%M")
        try:
            sheet = get_sheet()
            sheet.append_row([tanggal, keterangan, nominal])
            nominal_fmt = f"Rp{nominal:,}".replace(",", ".")
            await update.message.reply_text(
                f"Dicatat!\n"
                f"- {keterangan}\n"
                f"- {nominal_fmt}\n"
                f"- {tanggal}"
            )
        except Exception as e:
            await update.message.reply_text(f"Gagal menyimpan: {str(e)}")
    else:
        await update.message.reply_text(
            "Format tidak dikenali.\n"
            "Contoh yang benar: makan siang 35000"
        )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, catat))
app.run_polling()
