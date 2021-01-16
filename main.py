from modules import tg, secondchecker
import sys, re
exit = sys.exit
from telegram.ext import Updater, MessageHandler, CommandHandler, CallbackContext
from telegram.ext.filters import Filters
from telegram.error import InvalidToken
from telegram import ParseMode, Update

settings = {
    "each": {
        "min": 1,
        "max": 10,
    },
    "total": {
        "min": 0,
        "max": 1000000,
    },
    "feedback": {
        "FormatError": "Not a regular add second format\!",
        "TooManyError": "Too many seconds\! Please send seconds below `{}`\.",
        "TooSmallError": "Too small second count\! Please send seconds bigger then `{}`\.",
        "EnoughError": "That is enough\! Ask @emojiwiki to clear seconds\, use /limit to get limits\!",
        "Success": "Thank you for your second\! current seconds: `{}`",
        "StealError": "Trying to steal seconds from Him\, your life balance has been taken away by the elderly\. He will take half of the day\, forever\.",
        "Get": "Current seconds: `{}`",
        "LimitFeedBack": "Limits:\n\# Each donation\nmin: `{emin}`\nmax: `{emax}`\n\# Total\nmax: `{tmax}`"
    },
}

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
        try:
            result = re.search('\-(.*)s', update.message.text).group(1)
            update.message.reply_text(settings["feedback"]["StealError"],parse_mode=ParseMode.MARKDOWN_V2)
        except AttributeError:
            pass
        finally:
            return
    sec = load()
    addsec = 0
    try:
        addsec = int(result)
    except ValueError:
        update.message.reply_text(settings["feedback"]["FormatError"],parse_mode=ParseMode.MARKDOWN_V2)
        return
    if addsec > settings["each"]["max"]:
        update.message.reply_text(settings["feedback"]["TooManyError"].format(str(settings["each"]["max"])),parse_mode=ParseMode.MARKDOWN_V2)
        return
    if addsec < settings["each"]["min"]:
        update.message.reply_text(settings["feedback"]["TooSmallError"].format(str(settings["each"]["min"])),parse_mode=ParseMode.MARKDOWN_V2)
        return
    sec = sec + addsec
    if sec > settings["total"]["max"]:
        update.message.reply_text(settings["feedback"]["EnoughError"],parse_mode=ParseMode.MARKDOWN_V2)
        return
    update.message.reply_text(settings["feedback"]["Success"].format(str(sec)),parse_mode=ParseMode.MARKDOWN_V2)
    save(sec)

def get(update: Update, context: CallbackContext):
    update.message.reply_text(settings["feedback"]["Get"].format(str(load())),parse_mode=ParseMode.MARKDOWN_V2)

def limit(update: Update, context: CallbackContext):
    update.message.reply_text(settings["feedback"]["LimitFeedBack"].format(emin=settings["each"]["min"],emax=settings["each"]["max"],tmax=settings["total"]["max"],),parse_mode=ParseMode.MARKDOWN_V2)

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
    dp.add_handler(CommandHandler('limit', limit))
    dp.add_handler(MessageHandler(Filters.text, rawhandler))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
