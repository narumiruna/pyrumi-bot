from dotenv import load_dotenv
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

from pyrumi.tools.web import WebBrowser


def main():
    load_dotenv()
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-0613")
    tools = [
        ArxivQueryRun(),
        DuckDuckGoSearchRun(),
        PubmedQueryRun(),
        WebBrowser(),
        WolframAlphaQueryRun(api_wrapper=WolframAlphaAPIWrapper()),
        YouTubeSearchTool(),
    ]
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    agent = initialize_agent(tools=tools,
                             llm=llm,
                             agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                             memory=memory,
                             verbose=True)
    while True:
        try:
            question = input("User: ")
            resp = agent.run(question)
            print('Agent:', resp)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()
