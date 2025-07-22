import os
import requests
import urllib.parse
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
TOKEN = os.getenv("BOT_TOKEN")

def build_newsapi_url(query, from_date, to_date, language):
    enhanced_query = (
        f"({query}) AND "
        "(pelaajakaupat OR loukkaantumiset OR kokoonpano OR siirto OR trade OR injury OR lineup OR transfer OR coach)"
    )
    encoded_query = urllib.parse.quote_plus(enhanced_query)
    return (
        f"https://newsapi.org/v2/everything?"
        f"q={encoded_query}&"
        f"from={from_date}&"
        f"to={to_date}&"
        f"language={language}&"
        f"sortBy=publishedAt&"
        f"apiKey={NEWS_API_KEY}"
    )

async def uutiset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Käytä komentoa näin:\n/uutiset <aihe>\n"
            "Esimerkiksi:\n/uutiset jalkapallo\n/uutiset nhl"
        )
        return

    query = " ".join(context.args)
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

    urls = [
        build_newsapi_url(query, from_date, to_date, "fi"),
        build_newsapi_url(query, from_date, to_date, "en")
    ]

    all_articles = []
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            all_articles.extend(articles)

    if not all_articles:
        await update.message.reply_text("Ei löytynyt uutisia aiheesta.")
        return

    # Järjestä uusimmat ensin ja rajaa esim. 10 uutiseen
    sorted_articles = sorted(all_articles, key=lambda a: a.get("publishedAt", ""), reverse=True)[:10]

   reply_text = f"<b>Ajankohtaisia uutisia aiheesta {query}:</b>\n\n"
for article in sorted_articles:
    title = article.get("title", "Ei otsikkoa")
    url = article.get("url", "")
    reply_text += f"• <a href='{url}'>{title}</a>\n"

   await update.message.reply_text(reply_text, parse_mode="HTML", disable_web_page_preview=True)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("uutiset", uutiset))
    print("Botti käynnissä...")
    app.run_polling()
