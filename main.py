import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from commands.kerroinmuutokset import kerroinmuutokset
from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("kerroinmuutokset", kerroinmuutokset))
    print("Bot käynnissä...")
    app.run_polling()

if __name__ == '__main__':
    main()
