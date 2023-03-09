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


class ChatGPT:

    def __init__(self):
        self.dialogues = {}

    async def create(self, messages):
        return await openai.ChatCompletion.acreate(model="gpt-3.5-turbo", messages=messages)

    async def reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        reply_id = update.message.reply_to_message.message_id
        if reply_id not in self.dialogues.keys():
            logger.info('reply_id: {} not exists', reply_id)
            return
        else:
            messages = self.dialogues[reply_id]
        messages.append({'role': 'user', 'content': update.message.text})

        response = await self.create(messages)

        response_contents = []
        for i, choice in enumerate(response.choices):
            logger.info('#{} chatgpt: {}', i, choice.message.content)
            logger.info('#{} message: {}', i, choice.message)
            messages.append(dict(choice.message))
            response_contents.append(choice.message.content)

        new_message = await context.bot.send_message(chat_id=update.effective_chat.id,
                                                     text='\n'.join(response_contents),
                                                     reply_to_message_id=update.message.id)

        self.dialogues[new_message.message_id] = messages

        logger.info('messages: {}', messages)

    async def start_gpt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        messages = [{'role': 'user', 'content': update.message.text}]
        response = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo", messages=messages)

        response_contents = []
        for i, choice in enumerate(response.choices):
            logger.info('#{} chatgpt: {}', i, choice.message.content)
            logger.info('#{} message: {}', i, choice.message)
            messages.append(dict(choice.message))
            response_contents.append(choice.message.content)

        new_message = await context.bot.send_message(chat_id=update.effective_chat.id,
                                                     text='\n'.join(response_contents),
                                                     reply_to_message_id=update.message.id)

        logger.info('new message id: {}', new_message.message_id)
        logger.info('thread id: {}', new_message.message_thread_id)
        self.dialogues[new_message.message_id] = messages


if __name__ == '__main__':
    chatgtp = ChatGPT()

    logger.info('bot token: {}', BOT_TOKEN)
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    gpt_handler = CommandHandler('gpt', chatgtp.start_gpt)
    application.add_handler(gpt_handler)

    reply_handler = MessageHandler(filters.REPLY & filters.TEXT & (~filters.COMMAND), chatgtp.reply)
    application.add_handler(reply_handler)

    application.run_polling()
