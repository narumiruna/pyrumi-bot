import os
from typing import List
from typing import Optional

import openai
from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes


def join_content(messages):
    return '\n'.join([message['content'] for message in messages])


class ChatGPTBot:

    def __init__(self,
                 model_name: str = 'gpt-3.5-turbo',
                 whitelist: Optional[List[str]] = None,
                 system_content: Optional[str] = None):
        self.model_name = model_name
        self.whitelist = whitelist
        self.system_content = system_content

        self.dialogues = {}

    @classmethod
    def from_env(cls):
        whitelist = os.getenv('BOT_WHITELIST')
        openai.api_key = os.environ.get('OPENAI_API_KEY')

        if whitelist is not None:
            whitelist = [int(chat_id.strip()) for chat_id in whitelist.split(',')]

        return cls(whitelist=whitelist)

    def _is_valid(self, update: Update):
        if self.whitelist is None:
            return True

        return update.message.chat_id in self.whitelist

    async def _create(self, messages):
        response = await openai.ChatCompletion.acreate(model=self.model_name, messages=messages)
        return [dict(choice.message) for choice in response.choices]

    async def reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info('message: {}', update.message)
        if not self._is_valid(update):
            return

        reply_id = update.message.reply_to_message.message_id
        if reply_id not in self.dialogues.keys():
            logger.info('reply_id: {} not exists', reply_id)
            return

        messages = self.dialogues[reply_id] + [{'role': 'user', 'content': update.message.text}]
        response = await self._create(messages)

        chat_message = await context.bot.send_message(chat_id=update.effective_chat.id,
                                                      text=join_content(response),
                                                      reply_to_message_id=update.message.id)

        self.dialogues[chat_message.message_id] = messages + response

        logger.info('messages: {}', messages)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info('message: {}', update.message)
        if not self._is_valid(update):
            return

        messages = [{'role': 'user', 'content': update.message.text.rstrip('/gpt')}]
        # insert system content if exists
        if self.system_content is not None:
            messages = [{"role": "system", "content": self.system_content}] + messages

        response = await self._create(messages)

        chat_message = await context.bot.send_message(chat_id=update.effective_chat.id,
                                                      text=join_content(response),
                                                      reply_to_message_id=update.message.id)

        logger.info('new message id: {}', chat_message.message_id)
        logger.info('thread id: {}', chat_message.message_thread_id)
        self.dialogues[chat_message.message_id] = messages + response
