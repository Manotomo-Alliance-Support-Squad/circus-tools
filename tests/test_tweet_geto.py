from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import MagicMock, patch

from tools import tweet_geto


class TestGetApiObjWithAuth:

    @patch("tools.tweet_geto.TwitterOAuth")
    @patch("tools.tweet_geto.TwitterAPI")
    def test_auth_user_path(self, mock_api, mock_oauth):
        tmp_file = NamedTemporaryFile()
        tmp_filepath = Path(tmp_file.name)
        tweet_geto.get_api_obj_with_auth(Path(tmp_file.name))
        mock_oauth.read_file.assert_called_with(tmp_filepath.resolve())

    @patch("tools.tweet_geto.TwitterOAuth")
    @patch("tools.tweet_geto.TwitterAPI")
    def test_auth_default_path(self, mock_api, mock_oauth):
        tweet_geto.get_api_obj_with_auth()
        mock_oauth.read_file.assert_called_with()

    @patch("tools.tweet_geto.TwitterOAuth")
    @patch("tools.tweet_geto.TwitterAPI")
    def test_auth_user_path_not_file(self, mock_api, mock_oauth):
        tweet_geto.get_api_obj_with_auth(Path("asdf"))
        mock_oauth.read_file.assert_called_with()


# TODO: Patch TwitterPager to figure out if query is sent as we expect
# TODO: Patch TwitterOAuth to figure out if filepath is dealt with the correct way
# TODO: Patch TwitterAPI to figure out if the right auth informaion is pass through
class TestRecentSearchPager:

    def test_falsey_fields():
        pass

    def test_truthy_fields():
        pass

    def test_falsey_query():
        pass

    def test_truthy_query():
        pass


def test_dump_pager_content_to_json():
    pass
