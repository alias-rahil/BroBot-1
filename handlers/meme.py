import requests
import random
from misc.text import subreddits, meme_api
from telegram.ext import CommandHandler


def meme(update, context):
    options = subreddits
    choice = random.choice((options + ["all"]))
    if choice == "all":
        api = f"{meme_api}/{choice}"
        response = requests.get(api).json()
        while response["subreddit"] in options:
            response = requests.get(api).json()
    else:
        response = requests.get(f"{meme_api}/{choice}").json()
    update.message.reply_photo(response["url"], caption=response["title"])


meme_handler = CommandHandler("meme", meme)
