from telegram.ext import ApplicationBuilder, CommandHandler
from commands.ottelut import ottelut
from commands.kerroinmuutokset import kerroinmuutokset
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("ottelut", ottelut))
    app.add_handler(CommandHandler("kerroinmuutokset", kerroinmuutokset))

    app.run_polling()

if __name__ == "__main__":
    main()
