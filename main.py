import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Moi! Olen botti ja vastaan komentoihin. 🤖")
async def periodic_task(app):
    while True:
        try:
            await app.bot.send_message(chat_id=CHAT_ID, text="Terve! Tämä viesti lähetetään tunnin välein.")
        except TimedOut:
            print("Yhteys aikakatkaistu, yritetään uudestaan 30 sekunnin päästä.")
            await asyncio.sleep(30)
            continue  # yritetään uudestaan
        except Exception as e:
            print(f"Muu virhe: {e}")
        await asyncio.sleep(3600)  # odota tunti

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
# Käynnistä ajastettu tehtävä taustalle
    app.job_queue.run_repeating(lambda ctx: asyncio.create_task(periodic_task(app)), interval=3600, first=10)

if __name__ == "__main__":
    main()

