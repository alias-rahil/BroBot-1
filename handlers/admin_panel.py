from misc.text import (
    not_admin,
    ask_id,
    already_admin,
    add_success,
    repo_path,
    file_name,
    err_msg,
)
from telegram.ext import ConversationHandler, MessageHandler, CommandHandler, Filters
from telegram import ReplyKeyboardMarkup, ForceReply
from github import Github
from misc.invalid_msg import wrong_option
import os


def admin_panel(update, contex):
    options = [["List Admins"], ["Add Admin"]]
    update.message.reply_text(
        "Please select an option:",
        reply_markup=ReplyKeyboardMarkup(
            options, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return 0


def admin_options(update, context):
    option = update.message.text
    if option == "List Admins":
        try:
            update.message.reply_text(
                Github(os.getenv("API"))
                .get_repo(repo_path)
                .get_contents(file_name)
                .decoded_content.decode()
                .strip()
            )
            return ConversationHandler.END
        except BaseException:
            update.message.reply_text(err_msg)
            return ConversationHandler.END

    else:
        try:
            admin_list = (
                Github(os.getenv("API"))
                .get_repo(repo_path)
                .get_contents(file_name)
                .decoded_content.decode()
                .strip()
                .split("\n")
            )
            if str(update.message.from_user.id) in admin_list or (
                update.message.from_user.username
                and update.message.from_user.username.lower()
                in [i.lower() for i in admin_list]
            ):
                update.message.reply_text(ask_id, reply_markup=ForceReply())
                return 1
            else:
                update.message.reply_text(not_admin)
                return ConversationHandler.END
        except BaseException:
            update.message.reply_text(err_msg)
            return ConversationHandler.END


def add_admin(update, context):
    try:
        g = Github(os.getenv("API"))
        admin_list = [
            i.lower()
            for i in g.get_repo(repo_path)
            .get_contents(file_name)
            .decoded_content.decode()
            .strip()
            .split("\n")
        ]
        admin = update.message.text.lower().replace("@", "")
        if admin in admin_list:
            update.message.reply_text(admin + " " + already_admin)
        else:
            repo = g.get_repo(repo_path)
            contents = repo.get_contents(file_name)
            admin_list.append(admin)
            repo.update_file(
                contents.path,
                f"added-{admin}-as-admin",
                "\n".join(admin_list),
                contents.sha,
            )
            update.message.reply_text(admin + " " + add_success)
        return ConversationHandler.END
    except BaseException:
        update.message.reply_text(err_msg)
        return ConversationHandler.END


admin_states = {
    0: [MessageHandler(Filters.regex("^(List Admins|Add Admin)$"), admin_options)],
    1: [MessageHandler(Filters.text, add_admin)],
}
admin_handler = ConversationHandler(
    entry_points=[CommandHandler("adminpanel", admin_panel)],
    states=admin_states,
    fallbacks=[MessageHandler(Filters.all, wrong_option)],
)
