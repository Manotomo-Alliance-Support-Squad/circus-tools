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

    @pytest.mark.parametrize(
        'twitter_context, circus_context', [
            ('id', 'tweet_id'),
            ('name', 'display_name'),
            ('text', 'message'),
            ('username', 'username'),
        ]
    )
    def test_get_string_contexts(self, twitter_context, circus_context):
        """Tests that simple text context loads properly.
        circus_context is the intermediate context defined in tweet_context.TWEET_CONTEXT_MAPPING, mapping a
        human readable key to the path to the appropraite value in the tweet data model.
        """
        load_context = {
            circus_context: f'{twitter_context} truthy_context'
        }
        context_attribute = f'get_tweet_{twitter_context}'

        test_context = tweet_context.TweetContext(load_context)

        test_context_method = getattr(test_context, context_attribute)
        assert test_context_method() == f'{twitter_context} truthy_context'
