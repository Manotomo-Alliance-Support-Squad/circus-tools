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


def get_api_obj_with_auth(auth_filepath: Path = None):
    """Gets a TwitterAPI object using Twitter developer credentials.
    """
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
    """Gets an TwitterAPI object and hits the recent tweets endpoint to retrive a TwitterPager object.

    Example api_request
    aqua_api_request = {
        'query': {'#Ganbareあくたん -is:retweet'},
        'expansions': EXPANSIONS,
        'tweet.fields': TWEET_FIELDS,
        'media.fields': MEDIA_FIELDS,
    }

    """
    api = get_api_obj_with_auth(auth_filepath)

    if not isinstance(query, str):
        raise TypeError(f'query needs to be a str. Provided query is {query}')

    api_request = dict(**fields, **{'query': query})
    return TwitterPager(
        api,
        RECENT_TWEETS_ENDPOINT,
        api_request,
        hydrate_type=hydrate_type
    )


def dump_pager_content_to_json(pager: TwitterPager, filepath: Path):
    """Dumps a TwitterPager's content into a JSON file
    """
    if filepath.suffix != '.json':
        raise ValueError('Filetype should be a json file.')

    all_pager_results = [result for result in pager.get_iterator()]

    with open(filepath.resolve(), 'w') as fp:
        json.dump(all_pager_results, fp)
