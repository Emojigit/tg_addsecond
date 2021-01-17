import sys, re, logging
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
        "LimitFeedBack": "Limits:\n\# Each donation\nmin: `{emin}`\nmax: `{emax}`\n\# Total\nmax: `{tmax}`",
        "StickerFeedBack": "CAACAgUAAxkBAAMpYAJwIZSj8AVEmqtb1ngZb6tOpLgAAjYAA5sHqT6HF6eLr1hlsx4E",
    },
    "logging": {
        "level": logging.INFO,
        "format": "%(asctime)s %(levelname)s[%(name)s] %(message)s",
        "filename": "debug.txt",
    },
}
logging.basicConfig(level=settings["logging"]["level"],format=settings["logging"]["format"])
logger = {
    "SecondSaver": logging.getLogger("SecondSaver"),
    "TokenReader": logging.getLogger("TokenReader"),
    "MessageHandler": logging.getLogger("MessageHandler"),
    "CommandHandler": logging.getLogger("MessageHandler"),
    "MainScript": logging.getLogger("MainScript"),
    "root": logging.getLogger()
}
rootfh = logging.FileHandler("debug.txt")
rootfh.setFormatter(logging.Formatter(settings["logging"]["format"]))
logger["root"].addHandler(rootfh)

def load():
    try:
        with open("seconds.txt","r") as f:
            try:
                sec = int(f.read())
                logger["SecondSaver"].info("Got {} in seconds.txt".format(str(sec)))
                return sec
            except ValueError:
                logger["SecondSaver"].error("Error while loading seconds.txt : invalid int in the file")
                # print("[ERROR] Error while loading seconds.txt : invalid int in the file!")
                exit(2)
    except FileNotFoundError:
        logger["SecondSaver"].warning("No seconds.txt!")
        # print("[WARNING] No seconds.txt!")
        return 0

load()

def token():
    try:
        with open("token.txt","r") as f:
            return f.read().rstrip('\n')
    except FileNotFoundError:
        logger["TokenReader"].error("No token.txt!")
        # print("[ERROR] No token.txt!")
        exit(3)

def save(seconds):
    with open("seconds.txt","w+") as f:
        f.write(str(seconds))
    logger["SecondSaver"].info("written seconds!")

def rawhandler(update, context):
    result = ""
    try:
        result = re.search('\+(.*)s', update.message.text).group(1)
        logger["MessageHandler"].info("Got {} seconds".format(str(result)))
    except AttributeError:
        logger["MessageHandler"].warning("Get plus seconds failed, trying to get minus seconds")
        try:
            result = re.search('\-(.*)s', update.message.text).group(1)
            update.message.reply_text(settings["feedback"]["StealError"],parse_mode=ParseMode.MARKDOWN_V2)
            logger["MessageHandler"].info("Got {} minus seconds".format(str(result)))
        except AttributeError:
            logger["MessageHandler"].warning("Not a seconds operation!")
            pass
        finally:
            return
    sec = load()
    addsec = 0
    try:
        addsec = int(result)
    except ValueError:
        logger["MessageHandler"].warning("Wrong format while procession add seconds request")
        update.message.reply_text(settings["feedback"]["FormatError"],parse_mode=ParseMode.MARKDOWN_V2)
        return
    if addsec > settings["each"]["max"]:
        logger["MessageHandler"].warning("Too many seconds!")
        update.message.reply_text(settings["feedback"]["TooManyError"].format(str(settings["each"]["max"])),parse_mode=ParseMode.MARKDOWN_V2)
        return
    if addsec < settings["each"]["min"]:
        logger["MessageHandler"].warning("Too small add second request!")
        update.message.reply_text(settings["feedback"]["TooSmallError"].format(str(settings["each"]["min"])),parse_mode=ParseMode.MARKDOWN_V2)
        return
    sec = sec + addsec
    if sec > settings["total"]["max"]:
        logger["MessageHandler"].warning("Total seconds is enough!")
        update.message.reply_text(settings["feedback"]["EnoughError"],parse_mode=ParseMode.MARKDOWN_V2)
        return
    logger["MessageHandler"].info("Add second success! seconds now: {}".format(str(sec)))
    update.message.reply_text(settings["feedback"]["Success"].format(str(sec)),parse_mode=ParseMode.MARKDOWN_V2)
    save(sec)

def get(update: Update, context: CallbackContext):
    sec = str(load())
    logger["CommandHandler"].info("Got get command! seconds now: {}".format(sec))
    update.message.reply_text(settings["feedback"]["Get"].format(sec),parse_mode=ParseMode.MARKDOWN_V2)

def limit(update: Update, context: CallbackContext):
    logger["CommandHandler"].info("Got limit command!")
    update.message.reply_text(settings["feedback"]["LimitFeedBack"].format(emin=settings["each"]["min"],emax=settings["each"]["max"],tmax=settings["total"]["max"],),parse_mode=ParseMode.MARKDOWN_V2)

def sticker(update: Update, context: CallbackContext):
    logger["CommandHandler"].info("Got sticker command!")
    update.message.reply_sticker(settings["feedback"]["StickerFeedBack"])

def main():
    """Start the bot."""
    tok = token()
    try:
        updater = Updater(tok, use_context=True)
        logger["MainScript"].info("Get updater success!")
    except InvalidToken:
        logger["MainScript"].critical("Invalic Token! Plase edit token.txt and fill in a valid token.")
        raise
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('get', get))
    dp.add_handler(CommandHandler('limit', limit))
    dp.add_handler(CommandHandler('sticker', sticker))
    dp.add_handler(MessageHandler(Filters.text, rawhandler))
    updater.start_polling()
    logger["MainScript"].info("Started the bot! Use Ctrl-C to stop it.")
    updater.idle()


if __name__ == '__main__':
    main()
