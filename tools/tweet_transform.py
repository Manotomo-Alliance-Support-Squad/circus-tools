"""Tools to translate tweet JSONs to other data formats.
"""

from copy import deepcopy
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
            focus_entry_values = header_map[focus_entry](tweet_context)
            entry_dict = deepcopy(header_map)
            for key in header_map.keys():
                entry_dict[key] = header_map[key](tweet_context)

            # write tweets with artlink
            if focus_entry_values is not None and write_focus_entry:
                for value in focus_entry_values:
                    # Hardcording to make this work
                    if 'url' in value:
                        entry_dict[focus_entry] = value['url']
                    elif 'preview_image_url' in value:
                        entry_dict[focus_entry] = value['preview_image_url']
                    else:
                        # Purposefully do this so we can catch it at loading time
                        entry_dict[focus_entry] = None
                    csv_dict_writer.writerow(entry_dict)
            # write tweets without artlinks
            if focus_entry_values is None and write_non_focus_entry:
                entry_dict[focus_entry] = None
                csv_dict_writer.writerow(entry_dict)
