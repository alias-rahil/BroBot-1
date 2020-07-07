from misc.text import (
    ssh_start_command,
    empty_output,
    repo_path,
    file_name,
    err_msg,
    shell_msg,
    not_admin,
    key_api,
)
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
from misc.invalid_msg import wrong_option
from telegram import ForceReply
import subprocess
import threading
import time
import random
import ansistrip
from github import Github
from ast import literal_eval
from urllib.parse import quote_plus
import requests
import os

sessions = {}


def shell_session(update, context):
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
            os.system("cat /dev/zero | ssh-keygen -N '' || :")
            fs = open(f"{os.path.expanduser('~')}/.ssh/id_rsa.pub")
            pubkey = fs.read()
            fs.close()
            p = subprocess.Popen(
                f"{requests.get(key_api + quote_plus(pubkey)).text.strip()} {ssh_start_command}".split(),
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            sessions[update.message.from_user.id] = [p]
            sessions[update.message.from_user.id].append(
                threading.Thread(target=get_output, args=[update])
            )
            sessions[update.message.from_user.id].append("")
            sessions[update.message.from_user.id].append(
                threading.Thread(target=get_error, args=[update])
            )
            if random.choice([True, False]):
                sessions[update.message.from_user.id][3].start()
                time.sleep(1)
                sessions[update.message.from_user.id][1].start()
            else:
                sessions[update.message.from_user.id][1].start()
                time.sleep(1)
                sessions[update.message.from_user.id][3].start()
            time.sleep(1)
            text = sessions[update.message.from_user.id][2]
            sessions[update.message.from_user.id].append(
                sessions[update.message.from_user.id][2]
            )
            update.message.reply_text(shell_msg, reply_markup=ForceReply())
            return 0
        else:
            update.message.reply_text(not_admin)
            return ConversationHandler.END
    except BaseException:
        update.message.reply_text(err_msg)
        return ConversationHandler.END


def get_output(update):
    while sessions[update.message.from_user.id][0].poll() is None:
        sessions[update.message.from_user.id][2] = (
            sessions[update.message.from_user.id][2]
            + "\n"
            + sessions[update.message.from_user.id][0].stdout.readline().decode()
        ).strip()


def get_error(update):
    while sessions[update.message.from_user.id][0].poll() is None:
        sessions[update.message.from_user.id][2] = (
            sessions[update.message.from_user.id][2]
            + "\n"
            + sessions[update.message.from_user.id][0].stderr.readline().decode()
        ).strip()


def run_command(update, context):
    if update.message.text != "Force exit!":
        try:
            sessions[update.message.from_user.id][0].stdin.write(
                literal_eval(repr(update.message.text).replace("\\\\", "\\")).encode()
            )
            sessions[update.message.from_user.id][0].stdin.flush()
            time.sleep(2)
            text = ansistrip.ansi_strip(
                sessions[update.message.from_user.id][2].replace(
                    sessions[update.message.from_user.id][4], "", 1
                )
            )
            sessions[update.message.from_user.id][4] = sessions[
                update.message.from_user.id
            ][2]
            if sessions[update.message.from_user.id][0].poll() is None:
                update.message.reply_text(text, reply_markup=ForceReply())
                return 0
            else:
                update.message.reply_text(text)
                del sessions[update.message.from_user.id]
                return ConversationHandler.END
        except BaseException:
            if sessions[update.message.from_user.id][0].poll() is None:
                update.message.reply_text(empty_output, reply_markup=ForceReply())
                return 0
            else:
                update.message.reply_text(empty_output)
                del sessions[update.message.from_user.id]
                return ConversationHandler.END
    else:
        update.message.reply_text("Force exited the session!")
        del sessions[update.message.from_user.id]
        return ConversationHandler.END


ssh_states = {0: [MessageHandler(Filters.text, run_command)]}
ssh_handler = ConversationHandler(
    entry_points=[CommandHandler("shell", shell_session)],
    states=ssh_states,
    fallbacks=[MessageHandler(Filters.all, wrong_option)],
)
