"""Unit tests for tweet contexts and building tweet contexts
"""
import pytest

from tools import tweet_context


class TestTweetContext:

    def test_empty_context(self):
        """Tests that an empty context does not give us random default properties"""
        test_context = tweet_context.TweetContext(context_dict={})

        for attribute in vars(test_context):
            assert not getattr(test_context, attribute)

    @pytest.mark.parametrize('username, tweet_id', [('', 'mock_id'), ('mock_username', '')])
    def test_tweet_url_incomplete(self, username, tweet_id):
        """Tests that if there's missing parts of the url, an empty string is returned"""
        load_context = {'username': username, 'tweet_id': tweet_id}

        test_context = tweet_context.TweetContext(load_context)

        assert test_context.get_tweet_url() == ''
        assert test_context.get_tweet_url() == test_context.artistLink

    def test_media_without_url(self):
        """Tests that when there is no url for the media we don't load anything"""
        load_context = {
            'medias': [
                {'falsey_key_1': 'falsey_value_1'},
                {'falsey_key_2': 'falsey_value_2'},
            ]
        }

        test_context = tweet_context.TweetContext(load_context)

        assert test_context.get_tweet_media() == []
        assert test_context.get_tweet_media() == test_context.artworkLink

    @pytest.mark.parametrize('media_url_type', [tweet_context.MEDIA_URL_KEY, tweet_context.MEDIA_PREVIEW_URL_KEY])
    def test_get_tweet_media_singular(self, media_url_type):
        load_context = {
            'medias': [
                {media_url_type: 'truthy_media_url1'},
            ]
        }

        test_context = tweet_context.TweetContext(load_context)

        assert test_context.get_tweet_media() == ['truthy_media_url1']
        assert test_context.get_tweet_media() == test_context.artworkLink

    @pytest.mark.parametrize('media_url_type', [tweet_context.MEDIA_URL_KEY, tweet_context.MEDIA_PREVIEW_URL_KEY])
    def test_get_tweet_media_multiple(self, media_url_type):
        load_context = {
            'medias': [
                {media_url_type: 'truthy_media_url1'},
                {media_url_type: 'truthy_media_url2'},
            ]
        }

        test_context = tweet_context.TweetContext(load_context)

        assert test_context.get_tweet_media() == ['truthy_media_url1', 'truthy_media_url2']
        assert test_context.get_tweet_media() == test_context.artworkLink

    def test_get_tweet_media_multi_type(self):
        load_context = {
            'medias': [
                {tweet_context.MEDIA_URL_KEY: 'truthy_media_url1'},
                {tweet_context.MEDIA_PREVIEW_URL_KEY: 'truthy_media_preview_url1'},
            ]
        }

        test_context = tweet_context.TweetContext(load_context)

        assert test_context.get_tweet_media() == ['truthy_media_url1', 'truthy_media_preview_url1']
        assert test_context.get_tweet_media() == test_context.artworkLink
