import os
from typing import Optional

from langchain.agents import AgentType
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from .stock_tool import StockGetBestPerformingTool
from .stock_tool import StockPercentageChangeTool
from .stock_tool import StockPriceTool
from .whitelist import in_whitelist


class LangChainBot:
    chat_command: str = 'lc'

    def __init__(self, model_name: Optional[str] = None):
        self.llm = ChatOpenAI(model_name=model_name)
        self.tools = [StockPriceTool(), StockPercentageChangeTool(), StockGetBestPerformingTool()]

        self.agent = initialize_agent(self.tools, self.llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=False)

    @classmethod
    def from_env(cls):
        model_name = os.getenv('LANGCHAIN_MODEL_NAME', 'gpt-3.5-turbo-0613')
        return cls(model_name=model_name)

    async def chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not in_whitelist(update):
            return

        message = update.message.text.rstrip('/' + self.chat_command)

        agent_response = self.agent.run(message)

        bot_message = await context.bot.send_message(chat_id=update.effective_chat.id,
                                                     text=agent_response,
                                                     reply_to_message_id=update.message.id)
        logger.info('new message id: {}', bot_message.message_id)
        logger.info('thread id: {}', bot_message.message_thread_id)
