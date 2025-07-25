import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from commands.kerroinmuutokset import kerroinmuutokset
from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

import sys
from telegram.ext import ApplicationBuilder
from commands.kerroinmuutokset import kerroinmuutokset

def main():
    if getattr(sys, '_is_running', False):
        print("Bot already running!")
        return
    sys._is_running = True

    app = ApplicationBuilder().token("YOUR_BOT_TOKEN").build()
    app.add_handler(CommandHandler("kerroinmuutokset", kerroinmuutokset))
    app.run_polling()

if __name__ == "__main__":
    main()

