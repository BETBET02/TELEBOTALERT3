import os
from dotenv import load_dotenv

load_dotenv()  # Lataa .env-tiedoston arvot ympäristömuuttujiksi

from telegram.ext import ApplicationBuilder
from config import TELEGRAM_BOT_TOKEN
from commands.kerroinmuutokset import kerroinmuutokset
# muut importit...

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN)
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN ei ole asetettu ympäristömuuttujaan")

    app = ApplicationBuilder().token(token).build()

    # Lisää handlerit jne.


    app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()
    app.add_handler(CommandHandler("kerroinmuutokset", kerroinmuutokset))
    app.run_polling()

if __name__ == "__main__":
    main()

