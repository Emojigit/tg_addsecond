from modules import tg, secondchecker
import sys, re
exit = sys.exit
from telegram.ext import Updater, MessageHandler, CommandHandler, CallbackContext
from telegram.ext.filters import Filters
from telegram.error import InvalidToken
from telegram import ParseMode, Update

def load():
    try:
        with open("seconds.txt","r") as f:
            try:
                return int(f.read())
            except ValueError:
                print("[ERROR] Error while loading seconds.txt : invalid int in the file!")
                exit(2)
    except FileNotFoundError:
        print("[WARNING] No seconds.txt!")
        return 0

def token():
    try:
        with open("token.txt","r") as f:
            return f.read().rstrip('\n')
    except FileNotFoundError:
        print("[ERROR] No token.txt!")
        exit(3)

def save(seconds):
    with open("seconds.txt","w+") as f:
        f.write(str(seconds))

def rawhandler(update, context):
    result = ""
    try:
        result = re.search('\+(.*)s', update.message.text).group(1)
    except AttributeError:
        print("[WARNING] Got invalid plus second request")
        return
    sec = load()
    addsec = 0
    try:
        addsec = int(result)
    except ValueError:
        update.message.reply_text("not a regular add second format!")
        return
    sec = sec + addsec
    update.message.reply_text("Thank you for your second\! current seconds: `"+str(sec)+"`",parse_mode=ParseMode.MARKDOWN_V2)
    save(sec)

def get(update: Update, context: CallbackContext):
    update.message.reply_text('Current seconds: `{}`'.format(str(load())),parse_mode=ParseMode.MARKDOWN_V2)

def main():
    """Start the bot."""
    tok = token()
    try:
        updater = Updater(tok, use_context=True)
    except InvalidToken:
        print("[ERROR] Invalid token!")
        print("[ERROR] Token string:")
        print("[ERROR] "+tok)
        raise
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('get', get))
    dp.add_handler(MessageHandler(Filters.text, rawhandler))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
