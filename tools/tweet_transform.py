"""Tools to translate tweet JSONs to other data formats.
"""

from copy import deepcopy
import csv
import json
import logging
from pathlib import Path
from typing import Dict

from tweet_context import build_tweet_context

LOGGER = logging.getLogger(__name__)

HEADER_MAP = {
    "username": "",
    "artistLink": "",
    "artworkLink": "",
    "setID": "",
    "message": "",
}


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
