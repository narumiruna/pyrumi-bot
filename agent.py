from dotenv import load_dotenv
from langchain.agents import AgentType
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.tools import ArxivQueryRun
from langchain.tools import DuckDuckGoSearchRun
from langchain.tools import PubmedQueryRun
from langchain.tools import WolframAlphaQueryRun
from langchain.utilities.wolfram_alpha import WolframAlphaAPIWrapper


def main():
    load_dotenv()
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-0613")
    tools = [
        ArxivQueryRun(),
        DuckDuckGoSearchRun(),
        PubmedQueryRun(),
        WolframAlphaQueryRun(api_wrapper=WolframAlphaAPIWrapper()),
    ]
    agent = initialize_agent(tools=tools, llm=llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)
    while True:
        try:
            question = input("User: ")
            resp = agent.run(question)
            print('Agent:', resp)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()
