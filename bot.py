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
    creds_dict = json.loads(GOOGLE_CREDS.replace("\\n", "\n"))
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).sheet1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo! Kirim transaksi dengan format:\n"
        "keterangan nominal\n\n"
        "Contoh: makan siang 35000\n\n"
        "Command:\n"
        "/laporan - Ringkasan bulan ini"
    )

async def laporan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sheet = get_sheet()
        rows = sheet.get_all_values()

        if len(rows) <= 1:
            await update.message.reply_text("Belum ada transaksi yang dicatat.")
            return

        now = datetime.now()
        bulan_ini = now.strftime("%m/%Y")
        transaksi = []
        total = 0

        for row in rows[1:]:
            if len(row) >= 3:
                try:
                    nominal = int(row[2])
                except:
                    continue
                if bulan_ini in row[0]:
                    transaksi.append((row[0], row[1], nominal))
                    total += nominal

        if not transaksi:
            await update.message.reply_text(
                f"Tidak ada transaksi bulan {now.strftime('%m/%Y')}."
            )
            return

        bulan_nama = now.strftime("%B %Y")
        pesan = f"Laporan {bulan_nama}\n"
        pesan += "=" * 22 + "\n"
        for t in transaksi:
            nominal_fmt = f"Rp{t[2]:,}".replace(",", ".")
            pesan += f"- {t[1]}: {nominal_fmt}\n"
        total_fmt = f"Rp{total:,}".replace(",", ".")
        pesan += "=" * 22 + "\n"
        pesan += f"TOTAL: {total_fmt}\n"
        pesan += f"({len(transaksi)} transaksi)"

        await update.message.reply_text(pesan)

    except Exception as e:
        await update.message.reply_text(f"Gagal mengambil laporan: {str(e)}")

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
app.add_handler(CommandHandler("laporan", laporan))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, catat))
app.run_polling()
