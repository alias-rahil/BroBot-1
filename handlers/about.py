from misc.text import repo_link, image_link
from telegram.ext import CommandHandler


def about_website(update, context):
    update.message.reply_photo(image_link, caption=repo_link)


about_handler = CommandHandler("about", about_website)
