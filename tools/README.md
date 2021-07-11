# Tweet Getter (Ze KFP)

The tweet getter uses [TwitterAPI](https://github.com/geduldig/TwitterAPI) library for authentication, retrival, and transformation to data format used to load into our databases.

## Authentication

You will need twitter secrets, which you'll need to apply for [twitter developer account](https://developer.twitter.com/en/apply-for-access).

The functions in KFP relies on a credentials file that looks something like this
```
consumer_key=XXXXXXXXXXXXXXXXXXXXXXXXX
consumer_secret=YYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
access_token_key=ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ
access_token_secret=KUSAKUSAKUSAKUSAKUSAKUSAKUSAKUSA
```

You can name this as `credentials.txt` in the folder you are running the functions from, or specify the file in your function call.

## Getting a TweetPager for recent tweets

Using the `get_recent_search_pager` you can get a tweet pager for recent tweets. This works by providing a string query and [fields from the developer docs](https://developer.twitter.com/en/docs/twitter-api/fields).

To try a query, you do not need anything in the fields. However, for our purposes, we'll need the fields, so it does not have a default.

Example call:

```
example_pager = tweet_getto.get_recent_search_pager(
   query='example query',
   fields={}, 
   auth_filepath=Path("./credentials.txt")
)
```

You can see what options you have with the pager object you can see how to interact with a [TwitterPager at the official docs](http://geduldig.github.io/TwitterAPI/paging.html).

## Dumping pager contents to JSON

Once you have a pager you can dump the contents directly into a JSON file. All you need is the pager and a path you wish write to.

Example Call:

```
tweet_getto.dump_pager_content_to_json(
   example_pager,
   Path("./example.json")
)
```

**Note: There's nothing preventing you from overwriting a file that exists. Could be a feature to be added later.**

## Example

```
aqua_fields = {
   'expansions': 'author_id,attachments.media_keys'
   'tweet.fields': 'created_at,attachments,author_id'
   'media.fields': 'media_key,preview_image_url,type,url'
}

ganbare_pager = tweet_getto.get_recent_search_pager(
   '#Ganbareあくたん -is:retweet',
   aqua_fields,
   auth_filepath=Path("./credentials.txt"))

tweet_getto.dump_pager_content_to_json(
   ganbare_pager,
   Path("./060821_0330_ganbare.json")
)
```
