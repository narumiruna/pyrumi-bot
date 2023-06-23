import cloudscraper
from bs4 import BeautifulSoup
from langchain.tools import BaseTool


class WebBrowser(BaseTool):

    name = "web_browser"
    description = ('A web browser tool. '
                   'Input should be a url. '
                   'The output will be the text content of the website.')
    max_chars = 4000

    def _run(self, url: str) -> str:
        scraper = cloudscraper.create_scraper()
        resp = scraper.get(url)
        soup = BeautifulSoup(resp.text, 'html.parser')
        return soup.text.replace('\n', '').strip()[:self.max_chars]

    async def _arun(self, url: str) -> str:
        raise NotImplementedError("This tool does not support async")
