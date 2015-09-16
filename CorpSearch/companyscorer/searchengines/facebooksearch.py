import facebook

from trainer.social_profile import FacebookProfile
from trainer.social_post import FacebookPost
from simplediskcache.SimpleDiskCache import expiring_cache

# TODO: obtain from user.
access_token = "" # Removed.


class FacebookSearch(object):
    """Handles searching on Facebook."""

    @staticmethod
    def query(query):
        profiles = search_facebook(query)

        processed = []
        for profile in profiles:
            profile_id = profile['id']
            posts = posts_for(profile_id)
            processed.append(FacebookProfile(profile, posts))

        return processed

    @staticmethod
    def posts_for(profile_id):
        posts = posts_for(profile_id)
        return [FacebookPost(x) for x in posts]


@expiring_cache('facebook', 60*60*24*100)
def search_facebook(query, access_token=access_token):
    graph = facebook.GraphAPI(access_token=access_token)
    skeleton_graph_results = graph.request('/search', {
                                           'access_token': access_token,
                                           'q': query.encode('utf-8'),
                                           'type': 'page'
                                           })['data']

    graph_ids = [x['id'] for x in skeleton_graph_results][:20]
    if len(graph_ids):
        profiles = graph.get_objects(graph_ids).values()
    else:
        profiles = []

    return profiles


@expiring_cache('facebook_posts', 60*60*24*100)
def posts_for(profile_id, access_token=access_token):
    graph = facebook.GraphAPI(access_token=access_token)
    posts = graph.request('/v2.3/' + str(profile_id) + "/posts", {
                            'access_token': access_token,
                          })['data']

    if len(posts):
        return [x for x in posts if 'message' in x or 'description' in x]

    return []
