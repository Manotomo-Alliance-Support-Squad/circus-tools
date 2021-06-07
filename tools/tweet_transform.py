"""Tools to translate tweet JSONs to other data formats.
"""

import csv
import json
from pathlib import Path
from typing import Dict

TWEET_CONTEXT_MAPPING = {
    "username": ["author_id_hydrate", "username"],
    "display_name": ["author_id_hydrate", "name"],
    "text": "text",
    "medias": ["attachments", "media_keys_hydrate"],
    "tweet_id": "id",
}


def _get_username(context: Dict):
    return context.get("display_name")


def _get_artworkLink(context: Dict):
    return context.get("medias")


def _get_setID(context: Dict):
    return context.get("tweet_id")


def _get_message(context: Dict):
    return context.get("text")


def _get_artistLink(context: Dict):
    return f"https://twitter.com/{context.get('username')}/status/{context.get('tweet_id')}"


HEADER_MAP = {
    "username": _get_username,
    # link to tweet
    "artistLink": _get_artistLink,
    # Main iterator
    "artworkLink": _get_artworkLink,
    "setID": _get_setID,
    "message": _get_message,
}


def build_tweet_context(tweet: Dict) -> Dict:
    current_tweet_context = {}
    for context_key, context_path in TWEET_CONTEXT_MAPPING.items():
        if isinstance(context_path, str):
            current_tweet_context[context_key] = tweet[context_path]
        else:
            # Drill down to the level of content we want or set it to None if it doesn't exist
            current_node_context = tweet
            for node in context_path:
                current_node_context = current_node_context.get(node, None)
                if current_node_context is None:
                    break
            current_tweet_context[context_key] = current_node_context
    return current_tweet_context


def transform_tweet_json_to_csv(
    json_filepath: Path, unique_header: str, header_map: Dict = HEADER_MAP, csv_filepath: Path = None
):
    with open(json_filepath, 'r') as fp:
        tweets = json.load(fp)

    if csv_filepath is None:
        csv_filepath = json_filepath.parent.joinpath(json_filepath.stem + '.csv')

    tweet_contexts = map(build_tweet_context, tweets)
    with open(csv_filepath, 'w') as fp:
        csv.DictWriter(fp, fieldnames=list(header_map.keys()))
        for tweet_context in tweet_contexts:
            unique_value = header_map[unique_header](tweet_context)
            if unique_value is not None and unique_value.__iter__:
                # Is an iterable, need to loop
                pass
            else:
                # No media, just display some message and we're done
                pass
