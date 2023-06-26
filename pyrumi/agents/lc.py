import os
from typing import Optional

from langchain.agents import AgentType
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.tools import ArxivQueryRun
from langchain.tools import DuckDuckGoSearchRun
from langchain.tools import PubmedQueryRun
from langchain.tools import WolframAlphaQueryRun
from langchain.tools import YouTubeSearchTool
from langchain.utilities.wolfram_alpha import WolframAlphaAPIWrapper
from langtools import LoanCalculator
from langtools import VISAFXRate
from langtools import WebBrowser
from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from ..tools import StockGetBestPerformingTool
from ..tools import StockPercentageChangeTool
from ..tools import StockPriceTool
from ..whitelist import in_whitelist


class LangChainAgent:
    chat_command: str = 'lc'

    def __init__(self, model_name: Optional[str] = None):
        llm = ChatOpenAI(model_name=model_name)

        tools = [
            ArxivQueryRun(),
            DuckDuckGoSearchRun(),
            LoanCalculator(),
            PubmedQueryRun(),
            StockGetBestPerformingTool(),
            StockPercentageChangeTool(),
            StockPriceTool(),
            VISAFXRate(),
            WebBrowser(),
            WolframAlphaQueryRun(api_wrapper=WolframAlphaAPIWrapper()),
            YouTubeSearchTool(),
        ]

        memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
        self.agent = initialize_agent(tools=tools,
                                      llm=llm,
                                      agent=AgentType.OPENAI_FUNCTIONS,
                                      memory=memory,
                                      verbose=False)

    @classmethod
    def from_env(cls):
        model_name = os.getenv('LANGCHAIN_MODEL_NAME', 'gpt-3.5-turbo-0613')
        return cls(model_name=model_name)

    async def chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not in_whitelist(update):
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='Your chat ID {} is not in the whitelist.'.format(update.effective_chat.id),
                                     reply_to_message_id=update.message.id)
            return

        logger.info('update: {}', update)

        agent_resp = self.agent.run(update.message.text.rstrip('/' + self.chat_command))
        logger.info('agent response: {}', agent_resp)

        bot_resp = await context.bot.send_message(chat_id=update.effective_chat.id,
                                                  text=agent_resp,
                                                  reply_to_message_id=update.message.id)
        logger.info('bot response: {}', bot_resp)

    async def reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not in_whitelist(update):
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='Your chat ID {} is not in the whitelist.'.format(update.effective_chat.id),
                                     reply_to_message_id=update.message.id)
            return

        logger.info('update: {}', update)

        agent_resp = self.agent.run(update.message.text)
        logger.info('agent response: {}', agent_resp)

        bot_resp = await context.bot.send_message(chat_id=update.effective_chat.id,
                                                  text=agent_resp,
                                                  reply_to_message_id=update.message.id)
        logger.info('bot response: {}', bot_resp)
