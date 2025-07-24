from telegram.ext import CommandHandler
from commands.ottelut import ottelut
from commands.uutiset import uutiset
from commands.kertoimet import kertoimet

def register_handlers(app):
    app.add_handler(CommandHandler("ottelut", ottelut))
    app.add_handler(CommandHandler("uutiset", uutiset))
    app.add_handler(CommandHandler("kertoimet", kertoimet))
