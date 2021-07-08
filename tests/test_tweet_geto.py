from copy import deepcopy
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import patch

import pytest
from TwitterAPI import HydrateType

from tools import tweet_geto


class TestGetApiObjWithAuth:

    @patch('tools.tweet_geto.TwitterOAuth')
    @patch('tools.tweet_geto.TwitterAPI')
    def test_auth_default_path(self, mock_api, mock_oauth):
        tweet_geto.get_api_obj_with_auth()

        mock_oauth.read_file.assert_called_with()

    @patch('tools.tweet_geto.TwitterOAuth')
    @patch('tools.tweet_geto.TwitterAPI')
    def test_auth_user_path(self, mock_api, mock_oauth):
        tmp_file = NamedTemporaryFile()
        tmp_filepath = Path(tmp_file.name)

        tweet_geto.get_api_obj_with_auth(Path(tmp_file.name))

        mock_oauth.read_file.assert_called_with(tmp_filepath.resolve())

    @patch('tools.tweet_geto.TwitterOAuth')
    @patch('tools.tweet_geto.TwitterAPI')
    @pytest.mark.parametrize('test_path', [Path('not_file'), None])
    def test_auth_falsey_user_path(self, mock_api, mock_oauth, test_path):
        tweet_geto.get_api_obj_with_auth(test_path)

        mock_oauth.read_file.assert_called_with()


# TODO: Patch TwitterPager to figure out if query is sent as we expect
class TestRecentSearchPager:

    @patch('tools.tweet_geto.TwitterPager')
    @patch('tools.tweet_geto.get_api_obj_with_auth')
    def test_defaults(self, mock_get_api, mock_pager):
        """Tests hydrate_type and auth_filepath defautls"""
        expected_api_request = {'query': ''}

        tweet_geto.get_recent_search_pager(query='', fields={})

        mock_get_api.assert_called_with(None)
        mock_pager.assert_called_with(
            mock_get_api(),
            tweet_geto.RECENT_TWEETS_ENDPOINT,
            expected_api_request,
            hydrate_type=HydrateType.APPEND,  # default
        )

    @patch('tools.tweet_geto.TwitterPager')
    @patch('tools.tweet_geto.get_api_obj_with_auth')
    def test_auth_filepath(self, mock_get_api, mock_pager):
        """Tests non-default auth_filepath"""
        tweet_geto.get_recent_search_pager(query='', fields={}, auth_filepath=Path('asdf'))

        mock_get_api.assert_called_with(Path('asdf'))

    @patch('tools.tweet_geto.TwitterPager')
    @patch('tools.tweet_geto.get_api_obj_with_auth')
    @pytest.mark.parametrize('hydrate_type', [hydrate_type for hydrate_type in HydrateType])
    def test_hydrate_type(self, mock_get_api, mock_pager, hydrate_type):
        """Tests non-default hydrate_type"""
        tweet_geto.get_recent_search_pager(query='', fields={}, hydrate_type=hydrate_type)

        mock_pager.assert_called_with(
            mock_get_api(),
            tweet_geto.RECENT_TWEETS_ENDPOINT,
            {'query': ''},
            hydrate_type=hydrate_type,
        )

    @patch('tools.tweet_geto.TwitterPager')
    @patch('tools.tweet_geto.get_api_obj_with_auth')
    @pytest.mark.parametrize('field', ['string as field', ('tuple', 'as', 'field')])
    def test_falsey_fields(self, mock_get_api, mock_pager, field):
        with pytest.raises(TypeError):
            tweet_geto.get_recent_search_pager(query='', fields=field)

    @patch('tools.tweet_geto.TwitterPager')
    @patch('tools.tweet_geto.get_api_obj_with_auth')
    @pytest.mark.parametrize('field', [{}, {'expansions': 'author_id', 'tweet.fields': 'created_at'}])
    def test_truthy_fields(self, mock_get_api, mock_pager, field):
        expected_api_request = deepcopy(field)
        expected_api_request['query'] = ''  # should match query below

        tweet_geto.get_recent_search_pager(
            query=expected_api_request['query'], fields=field)

        mock_pager.assert_called_with(
            mock_get_api(),
            tweet_geto.RECENT_TWEETS_ENDPOINT,
            expected_api_request,
            hydrate_type=HydrateType.APPEND,  # default
        )

    @patch('tools.tweet_geto.TwitterPager')
    @patch('tools.tweet_geto.get_api_obj_with_auth')
    @pytest.mark.parametrize('query', [{'query': 'dict as query'}, ('tuple', 'as', 'query')])
    def test_falsey_query(self, mock_get_api, mock_pager, query):
        with pytest.raises(TypeError):
            tweet_geto.get_recent_search_pager(query=query, fields={})

    @patch('tools.tweet_geto.TwitterPager')
    @patch('tools.tweet_geto.get_api_obj_with_auth')
    def test_truthy_query(self, mock_get_api, mock_pager):
        expected_api_request = {'query': "polka oruka"}  # should match query below

        tweet_geto.get_recent_search_pager(
            query=expected_api_request['query'], fields={})

        mock_pager.assert_called_with(
            mock_get_api(),
            tweet_geto.RECENT_TWEETS_ENDPOINT,
            expected_api_request,
            hydrate_type=HydrateType.APPEND,  # default
        )

class TestDumpPagerContentToJson:

    def test_not_json_input(self):
        pass
