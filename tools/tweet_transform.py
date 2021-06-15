"""Tools to translate tweet JSONs to other data formats.
"""

from copy import deepcopy
import csv
import json
import logging
from pathlib import Path
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

HEADER_MAP = {
    "username": "",
    "artistLink": "",
    "artworkLink": "",
    "setID": "",
    "message": "",
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

    # Manotomo-vocab getters
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


# TODO: we want to build a transform_json_to_csv where we can give a description of json and how it maps to csv
# Issue is that we'll need to get multiple layer 
def transform_tweet_json_to_csv(
    json_filepath: Path, focus_entry: str, header_map: Dict = HEADER_MAP, csv_filepath: Path = None,
    write_focus_entry: bool = False, write_non_focus_entry: bool = False
):
    with open(json_filepath, 'r') as fp:
        tweets = json.load(fp)

    if csv_filepath is None:
        csv_filepath = json_filepath.parent.joinpath(json_filepath.stem + '.csv')

    tweet_contexts = map(build_tweet_context, tweets)

    with open(csv_filepath, 'w') as fp:
        csv_dict_writer = csv.DictWriter(fp, fieldnames=list(header_map.keys()))
        csv_dict_writer.writeheader()

        for tweet_context in tweet_contexts:

            focus_entry_values = getattr(tweet_context, focus_entry)
            entry_dict = deepcopy(header_map)
            for key in header_map.keys():
                entry_dict[key] = getattr(tweet_context, key)

            # write tweets with artlink
            if focus_entry_values is not None and write_focus_entry:
                for value in focus_entry_values:
                    entry_dict[focus_entry] = value
                    csv_dict_writer.writerow(entry_dict)
            # write tweets without artlinks
            if focus_entry_values is None and write_non_focus_entry:
                entry_dict[focus_entry] = None
                csv_dict_writer.writerow(entry_dict)
