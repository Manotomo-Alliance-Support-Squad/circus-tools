"""Exposes tweet metadata without the user needing to understand the twitter data model
"""

import logging
from pprint import pformat
from typing import Dict, List


LOGGER = logging.getLogger(__name__)


TWEET_CONTEXT_MAPPING = {
    'username': ['author_id_hydrate', 'username'],
    'display_name': ['author_id_hydrate', 'name'],
    'text': ['text'],
    'medias': ['attachments', 'media_keys_hydrate'],
    'tweet_id': ['id'],
    'datetime': ['created_at']
}
MEDIA_PREVIEW_URL_KEY = 'preview_image_url'
MEDIA_URL_KEY = 'url'


class TweetContext(object):
    """Object that maps the tweet data model into a dataclass like object"""

    def __init__(self, context_dict: Dict):
        self.context = context_dict

    def __repr__(self):
        return pformat(self.context)

    #  Twitter-vocab getters
    def get_tweet_id(self) -> str:
        return self.context.get('tweet_id')

    def get_tweet_name(self) -> str:
        return self.context.get('display_name')

    def get_tweet_media(self) -> List:
        """There could be more than one piece of media"""
        medias = self.context.get('medias')

        if medias is None:
            return None

        media_urls = []
        for media in medias:
            if MEDIA_PREVIEW_URL_KEY in media:
                media_urls.append(media[MEDIA_PREVIEW_URL_KEY])
            elif MEDIA_URL_KEY in media:
                media_urls.append(media[MEDIA_URL_KEY])
            else:
                LOGGER.warning(f'Media did not have preview_image_url or url in its keys. Media: {pformat(media)}')

        return media_urls

    def get_tweet_text(self) -> str:
        return self.context.get('text')

    def get_tweet_url(self) -> str:
        username = self.context.get('username')
        tweet_id = self.context.get('tweet_id')
        if not username or not tweet_id:
            LOGGER.warning(f'Missing username or tweet id; username: {username}, tweet_id: {tweet_id}')
            return ''
        return f"https://twitter.com/{username}/status/{tweet_id}"

    def get_tweet_username(self) -> str:
        """Not the same as the manotomo username, manotomo uses the display name"""
        return self.context.get('username')

    # Manotomo-vocab getters, matches db column names
    @property
    def username(self) -> str:
        """Gets the displayed name, username for twitter is a different thing"""
        return self.get_tweet_name()

    @property
    def artworkLink(self) -> List:
        """There could be more than one piece of media so this returns a List"""
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
