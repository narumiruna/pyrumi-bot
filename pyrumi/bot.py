import os

from dotenv import load_dotenv
from loguru import logger
from telegram import Update
from telegram.ext import ApplicationBuilder
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes

ECHO_COMMAND = 'echo'


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logger.info('message: {}', update.message)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=update.message.text.lstrip('/' + ECHO_COMMAND),
                                   reply_to_message_id=update.message.id)


def start_bot():
    load_dotenv()

    bot_token = os.environ.get('BOT_TOKEN')
    if bot_token is None:
        raise ValueError('BOT_TOKEN is not set')

    application = ApplicationBuilder().token(bot_token).build()

    echo_handler = CommandHandler(ECHO_COMMAND, echo)
    application.add_handler(echo_handler)
    application.run_polling()
