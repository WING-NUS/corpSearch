import tweepy

from trainer.social_profile import TwitterProfile
from trainer.social_post import TwitterPost
from simplediskcache.SimpleDiskCache import expiring_cache

# TODO: move into config file.
key = '' # Removed.
secret = '' # Removed.

# TODO: obtain from user.
access_token = '' # Removed.
access_token_secret = '' # Removed.


class TwitterSearch(object):
    """Handles searching on Twitter."""

    @staticmethod
    def query(query):
        """Given a query, returns Twitter profiles
        corresponding to that query."""
        profiles = search_twitter(query)

        processed = []
        for profile in profiles:
            profile_id = profile['id']
            posts = (posts_for(profile_id)
                     if not profile['protected'] else [])
            processed.append(TwitterProfile(profile, posts))

        return processed

    @staticmethod
    def posts_for(profile_id):
        """Given a Twitter profile ID, returns posts by that profile."""
        posts = posts_for(profile_id)
        return [TwitterPost(x) for x in posts]


@expiring_cache('twitter', 60*60*24*100)
def search_twitter(query,
                   access_token=access_token,
                   access_token_secret=access_token_secret):
    """Given a query, access token, and access token secret,
    searches Twitter for pages matching that query. Uses an expiring cache."""
    api = get_api(access_token, access_token_secret)

    return [x._json for x in api.search_users(query)]


@expiring_cache('twitter_posts', 60*60*24*100)
def posts_for(profile_id,
              access_token=access_token,
              access_token_secret=access_token_secret):
    """Gets the latest 20 posts for the user with the given ID.
    Uses an expiring cache."""
    api = get_api()

    try:
        posts = api.user_timeline(user_id=profile_id)
        return [x._json for x in posts]
    except tweepy.error.TweepError:
        return []


def get_api(access_token=access_token,
            access_token_secret=access_token_secret):
    """Initializes a tweepy-based Twitter API object for a given
    access token and secret."""
    auth = tweepy.OAuthHandler(consumer_key=key,
                               consumer_secret=secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)

    return api
