import os
from typing import List

from telegram import Update

whitelist = None


def in_whitelist(update: Update):
    global whitelist
    if whitelist is None:
        whitelist = WhiteList.from_env()
    return whitelist.is_valid(update)


class WhiteList:

    def __init__(self, whitelist: List[str] = None):
        self.whitelist = whitelist

    def is_valid(self, update: Update):
        if self.whitelist is None:
            return True

        return update.message.chat_id in self.whitelist

    @classmethod
    def from_env(cls):
        whitelist = os.getenv('BOT_WHITELIST')

        if whitelist is not None:
            whitelist = [int(chat_id.strip()) for chat_id in whitelist.split(',')]

        return cls(whitelist=whitelist)
