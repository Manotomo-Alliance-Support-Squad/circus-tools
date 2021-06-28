"""Exposes tweet metadata without traversals the user needing to understand the twitter data model
"""

import logging
from pprint import pformat
from typing import Dict, List


LOGGER = logging.getLogger(__name__)


TWEET_CONTEXT_MAPPING = {
    "username": ["author_id_hydrate", "username"],
    "display_name": ["author_id_hydrate", "name"],
    "text": ["text"],
    "medias": ["attachments", "media_keys_hydrate"],
    "tweet_id": ["id"],
    "datetime": ["created_at"]
}


class TweetContext(object):
    """docstring for TweetContext"""

    def __init__(self, context_dict: Dict):
        self.context = context_dict

    def __repr__(self):
        return pformat(self.context)

    #  Tweet-vocab getters
    def get_tweet_id(self) -> str:
        return self.context.get("tweet_id")

    def get_tweet_name(self) -> str:
        return self.context.get("display_name")

    def get_tweet_media(self) -> List:
        """There could be more than one piece of media"""
        medias = self.context.get("medias")
        if medias is None:
            return None
        media_urls = []
        for media in medias:
            if "preview_image_url" in media:
                media_urls.append(media["preview_image_url"])
            elif "url" in media:
                media_urls.append(media["url"])
            else:
                LOGGER.warning(f"Media did not have preview_image_url or url in its keys. Media: {pformat(media)}")

        return media_urls

    def get_tweet_text(self) -> str:
        return self.context.get("text")

    def get_tweet_url(self) -> str:
        return f"https://twitter.com/{self.context.get('username')}/status/{self.context.get('tweet_id')}"

    # Manotomo-vocab getters, matches db column names
    @property
    def username(self) -> str:
        return self.get_tweet_name()

    @property
    def artworkLink(self) -> List:
        """There could be more than one piece of media"""
        return self.get_tweet_media()

    @property
    def artistLink(self) -> str:
        return self.get_tweet_url()

    @property
    def setID(self) -> str:
        return self.get_tweet_id()

    @property
    def message(self) -> str:
        return self.get_tweet_text()


def build_tweet_context(tweet: Dict) -> TweetContext:
    """Takes a tweet format and transforms the context into how we map our DBs.
    """
    current_tweet_context = {}
    for context_key, context_path in TWEET_CONTEXT_MAPPING.items():
        if len(context_path) == 1:
            # Top level context
            current_tweet_context[context_key] = tweet[context_path[0]]
        else:
            # Drill down to the level of content we want or set it to None if it doesn't exist
            current_node_context = tweet.get(context_path[0])
            for node in context_path[1:]:
                if current_node_context is None:
                    break
                current_node_context = current_node_context.get(node)
            current_tweet_context[context_key] = current_node_context
    return TweetContext(current_tweet_context)
