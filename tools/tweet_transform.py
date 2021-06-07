"""Tools to translate tweet JSONs to other data formats.
"""

import csv
import json
from pathlib import Path
from typing import Dict

mapping = {
    "username": "display_name",
    "link": [["username"], ["id"]]
    "msg": [["text"]],
    "images": [["attachments", "media_keys_hydrate", "url"]],


}

master_map = {
    "username": ["author_id_hydrate", "username"],
    "display_name": ["author_id_hydrate", "name"],
    "text": "text",
    "medias": ["attachments", "media_keys_hydrate"],
    "tweet_id": "id",
}


def build_tweet_context(tweet: Dict) -> Dict:
    current_tweet_context = {}
    for context_key, context_path in master_map.items():
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


def transform_tweet_json_to_csv(json_filepath: Path, header_map: Dict, csv_filepath: Path = None):
    with open(json_filepath, 'r') as fp:
        tweets = json.load(fp)

    if csv_filepath is None:
        csv_filepath = json_filepath.parent.joinpath(json_filepath.stem + '.csv')

    tweet_contexts = map(build_tweet_context, tweets)
    with open(csv_filepath, 'w') as fp:
        csv.writer(fp, delimiter=",", fieldnames=list(header_map.keys()))
        
