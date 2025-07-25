from telegram.ext import ApplicationBuilder, CommandHandler
from commands.kerroinmuutokset import kerroinmuutokset
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    app.add_handler(CommandHandler("kerroinmuutokset", kerroinmuutokset))

from commands.ottelut import ottelut
app.add_handler(CommandHandler("ottelut", ottelut))

app.run_polling()

if __name__ == "__main__":
    main()
