"""Convinience functions for getting tweets
"""

import json
from pathlib import Path
from typing import Dict

from TwitterAPI import HydrateType, TwitterAPI, TwitterOAuth, TwitterPager, OAuthType

EXPANSIONS = 'author_id,attachments.media_keys'
TWEET_FIELDS = 'created_at,attachments,author_id'
MEDIA_FIELDS = 'media_key,preview_image_url,type,url'

RECENT_TWEETS_ENDPOINT = 'tweets/search/recent'

aqua_query = {
    # TODO: Add in a query limit for datetime
    'query': {'#Ganbareあくたん -is:retweet'},
    'expansions': EXPANSIONS,
    'tweet.fields': TWEET_FIELDS,
    'media.fields': MEDIA_FIELDS,
}


def get_api_obj_with_auth(auth_filepath: Path = None):
    # When auth_filepath is None, it looks for a credentials.txt in the dir of the current file
    if auth_filepath is not None and auth_filepath.is_file():
        auth = TwitterOAuth.read_file(auth_filepath.resolve())
    else:
        auth = TwitterOAuth.read_file()

    return TwitterAPI(auth.consumer_key, auth.consumer_secret, auth_type=OAuthType.OAUTH2, api_version='2')


def get_recent_search_pager(
    query: str,
    fields: Dict,
    auth_filepath: Path = None,
    hydrate_type: HydrateType = HydrateType.APPEND
) -> TwitterPager:
    api = get_api_obj_with_auth(auth_filepath)

    api_request = dict(**fields, **{'query': query})
    return TwitterPager(
        api,
        RECENT_TWEETS_ENDPOINT,
        api_request,
        hydrate_type=hydrate_type
    )


def dump_pager_content_to_json(pager: TwitterPager, filepath: Path):
    if filepath.suffix != '.json':
        raise ValueError('Filetype should be a json file.')

    all_pager_results = [result for result in pager.get_iterator()]

    with open(filepath.resolve(), 'w') as fp:
        json.dump(all_pager_results, fp)


# FIXME: This doesn't work as intended
def append_pager_content_to_json(
    pager: TwitterPager, filepath: Path, remove_dups: bool = False, no_bak_file: bool = False
):
    """Appends a pagers content to an already existing file. Note that remove_dups will remove any dups.

    In case of any unintended file changes, a .bak of the original file is dropped into the location the file is
    read from.
    """
    with open(filepath, 'r') as fp:
        current_results = json.load(fp)

    if not no_bak_file:
        bak_name = filepath.name + '.bak'
        filepath.rename(filepath.parent.joinpath(bak_name))

    for result in pager.get_iterator():
        current_results.append(result)

    # FIXME: doesn't work since dicts are in JSONs and are unhashable
    if remove_dups:
        list(set(current_results))

    with open(filepath, 'w') as fp:
        json.dump(current_results, fp)
