from enum import Enum
from typing import Optional
from typing import Type

from langchain.tools import BaseTool
from pornhub_api import PornhubApi
from pornhub_api.exceptions import NoVideoError
from pornhub_api.schemas.video import Video
from pydantic import BaseModel
from pydantic import Field


class OrderingEnum(str, Enum):
    featured = 'featured'
    newest = 'newest'
    mostviewed = 'mostviewed'
    rating = 'rating'


class PornHubSearchInput(BaseModel):
    query: str = Field(description='The query string.')
    ordering: OrderingEnum = Field(description='The ordering of the results.')


def to_string(video: Video) -> str:
    tags = ','.join([tag.tag_name for tag in video.tags])
    categories = ','.join([category.category for category in video.categories])
    pornstars = ','.join([pornstar.pornstar_name for pornstar in video.pornstars])
    return (f'Title: {video.title}\n'
            f'Views: {video.views}\n'
            f'Rating: {video.rating}\n'
            f'URL: {video.url}\n'
            f'Publish_date: {video.publish_date}\n'
            f'Categories: {categories}\n'
            f'Tags: {tags}\n'
            f'Pornstars: {pornstars}\n')


class PornHubSearchRun(BaseTool):

    name = "pornhub_search"
    description = ('A Pornbub search tool.'
                   'Input should be a query string. '
                   'The output will be a list of videos.')

    max_chars: Optional[int] = 4000
    max_videos: Optional[int] = 5
    args_schema: Optional[Type[BaseModel]] = PornHubSearchInput

    def _run(self, query: str, ordering: str) -> str:
        try:
            videos = PornhubApi().search.search_videos(q=query, ordering=ordering)
        except NoVideoError:
            return 'No videos found.'

        videos = videos[:self.max_videos]
        docs = [to_string(video) for video in videos]
        return '\n\n'.join(docs)[:self.max_chars]

    async def _arun(self, url: str) -> str:
        raise NotImplementedError("This tool does not support async")
