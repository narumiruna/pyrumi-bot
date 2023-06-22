from dotenv import load_dotenv
from langchain.agents import AgentType
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.tools import ArxivQueryRun
from langchain.tools import ClickTool
from langchain.tools import CurrentWebPageTool
from langchain.tools import DuckDuckGoSearchRun
from langchain.tools import ExtractHyperlinksTool
from langchain.tools import ExtractTextTool
from langchain.tools import GetElementsTool
from langchain.tools import NavigateBackTool
from langchain.tools import NavigateTool
from langchain.tools import PubmedQueryRun


def main():
    load_dotenv()
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-0613")
    tools = [
        DuckDuckGoSearchRun(),
        PubmedQueryRun(),
        ArxivQueryRun(),

        # playwright
        ClickTool(),
        CurrentWebPageTool(),
        ExtractHyperlinksTool(),
        ExtractTextTool(),
        GetElementsTool(),
        NavigateBackTool(),
        NavigateTool(),
    ]
    agent = initialize_agent(tools=tools, llm=llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)
    while True:
        try:
            question = input("User: ")
            resp = agent(question)
            print('Agent:', resp)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()
