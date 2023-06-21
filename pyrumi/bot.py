import html
import json
import os
import traceback

from dotenv import load_dotenv
from loguru import logger
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder
from telegram.ext import BaseHandler
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import MessageHandler
from telegram.ext import filters

from .chatgpt_bot import ChatGPTBot
from .langchain_bot import LangChainBot

ECHO_COMMAND = 'echo'
DEVELOPER_CHAT_ID = 102825484


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logger.info('message: {}', update.message)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=update.message.text.lstrip('/' + ECHO_COMMAND),
                                   reply_to_message_id=update.message.id)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (f"An exception was raised while handling an update\n"
               f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
               "</pre>\n\n"
               f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
               f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
               f"<pre>{html.escape(tb_string)}</pre>")

    # Finally, send the message
    await context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)


def start_bot():
    load_dotenv('.env')

    bot_token = os.environ.get('BOT_TOKEN')
    if bot_token is None:
        raise ValueError('BOT_TOKEN is not set')

    application = ApplicationBuilder().token(bot_token).build()

    application.add_error_handler(error_handler)

    # echo command
    application.add_handler(CommandHandler(ECHO_COMMAND, echo))

    # add chatgpt bot
    chatgpt_bot = ChatGPTBot.from_env()
    application.add_handler(CommandHandler('g', chatgpt_bot.start))
    application.add_handler(MessageHandler(filters.REPLY & filters.TEXT & (~filters.COMMAND), chatgpt_bot.reply))

    # add langchain bot
    langchain_bot = LangChainBot.from_env()
    application.add_handler(CommandHandler(langchain_bot.chat_command, langchain_bot.chat))

    application.run_polling()
