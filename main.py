from telegram.ext import ApplicationBuilder, CommandHandler
from commands.ottelut import ottelut
from commands.kerroinmuutokset import kerroinmuutokset
import logging
import os

logging.basicConfig(level=logging.INFO)

# Vain Render: suoraan ympäristömuuttujasta ilman dotenv
TOKEN = os.environ["TELEGRAM_TOKEN"]
print("DEBUG TOKEN:", TOKEN)  # Tarkista tulostuuko oikea token!

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("ottelut", ottelut))
    app.add_handler(CommandHandler("kerroinmuutokset", kerroinmuutokset))

    app.run_polling()

if __name__ == "__main__":
    main()
