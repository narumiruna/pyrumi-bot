import os

import openai
from loguru import logger
from telegram import Update
from telegram.ext import ApplicationBuilder
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes
from telegram.ext import MessageHandler
from telegram.ext import filters

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
openai.api_key = os.environ.get('OPENAI_API_KEY')


def join_content(messages):
    return '\n'.join([message['content'] for message in messages])


class ChatGPT:

    def __init__(self):
        self.dialogues = {}

    def is_valid(self, update: Update):
        return update.message.chat_id in [-1001970525344, 102825484]

    async def create(self, messages):
        response = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo", messages=messages)
        return [dict(choice.message) for choice in response.choices]

    async def reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info('message: {}', update.message)
        if not self.is_valid(update):
            return

        reply_id = update.message.reply_to_message.message_id
        if reply_id not in self.dialogues.keys():
            logger.info('reply_id: {} not exists', reply_id)
            return

        messages = self.dialogues[reply_id] + [{'role': 'user', 'content': update.message.text}]
        response = await self.create(messages)

        chat_message = await context.bot.send_message(chat_id=update.effective_chat.id,
                                                      text=join_content(response),
                                                      reply_to_message_id=update.message.id)

        self.dialogues[chat_message.message_id] = messages + response

        logger.info('messages: {}', messages)

    async def start_gpt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info('message: {}', update.message)
        if not self.is_valid(update):
            return

        messages = [{
            "role": "system",
            "content": "你會在每句話的後面加上ぺこ。你只會使用繁體中文、日文或者是英文。"
        }, {
            'role': 'user',
            'content': update.message.text.rstrip('/gpt')
        }]
        response = await self.create(messages)

        chat_message = await context.bot.send_message(chat_id=update.effective_chat.id,
                                                      text=join_content(response),
                                                      reply_to_message_id=update.message.id)

        logger.info('new message id: {}', chat_message.message_id)
        logger.info('thread id: {}', chat_message.message_thread_id)
        self.dialogues[chat_message.message_id] = messages + response


if __name__ == '__main__':
    chatgtp = ChatGPT()

    logger.info('bot token: {}', BOT_TOKEN)
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    gpt_handler = CommandHandler('gpt', chatgtp.start_gpt)
    application.add_handler(gpt_handler)

    reply_handler = MessageHandler(filters.REPLY & filters.TEXT & (~filters.COMMAND), chatgtp.reply)
    application.add_handler(reply_handler)

    application.run_polling()
