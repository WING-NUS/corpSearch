import abc

from urlresolver import UrlResolver
from social_post import TwitterPost, FacebookPost


class ProfileBase(object):
    """Represents a generic profile on a social network. This class should
    be inherited from to provide `convert_to_feature_vector` for all
    social networks."""
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def display_name(self):
        return 'Display Name'

    @abc.abstractproperty
    def handle(self):
        return 'Handle (Username)'

    @abc.abstractproperty
    def description(self):
        return 'Description'

    @abc.abstractproperty
    def urls(self):
        return ['Url']

    @abc.abstractproperty
    def profile_pic_link(self):
        return None

    @abc.abstractproperty
    def popularity(self):
        return -1

    def posts(self):
        return self.posts

    def to_dict(self):
        """Converts this profile to a dict, by giving the raw backing data."""
        return self.backing_data


class TwitterProfile(ProfileBase):
    """Represents a Twitter profile."""

    def __init__(self, raw_profile, posts):
        self.backing_data = raw_profile
        self.posts = [TwitterPost(x) for x in posts]

    @property
    def display_name(self):
        return self.backing_data.get('name', '')

    @property
    def handle(self):
        return self.backing_data['screen_name']

    @property
    def description(self):
        return self.backing_data.get('description', '')

    @property
    def urls(self):
        if 'entities' in self.backing_data and 'url' in self.backing_data['entities']:
            return [self.backing_data['entities']['url']['urls'][0]['expanded_url']]

        url_field = [self.backing_data['url']] if 'url' in self.backing_data else []
        shortened_urls = [x for x in url_field if x is not None]
        urls = [UrlResolver.resolve_shortened_url(x) for x in shortened_urls]
        return urls

    @property
    def profile_pic_link(self):
        return self.backing_data.get('profile_image_url', None)

    @property
    def popularity(self):
        return self.backing_data['followers_count']


class FacebookProfile(ProfileBase):
    """Represents a Facebook profile."""

    def __init__(self, raw_profile, posts):
        self.backing_data = raw_profile
        self.posts = [FacebookPost(x) for x in posts]

    @property
    def display_name(self):
        return self.backing_data['name']

    @property
    def handle(self):
        key = 'username' if 'username' in self.backing_data else 'id'

        return self.backing_data[key]

    @property
    def description(self):
        # There's either About, Description, or both.
        # TODO: handle company_overview.
        concatenated = ''

        if 'about' in self.backing_data:
            concatenated += self.backing_data['about']
            concatenated += '\n'

        if 'description' in self.backing_data:
            concatenated += self.backing_data['description']

        return concatenated

    @property
    def urls(self):
        urls = []
        if 'website' in self.backing_data:
            urls = self.backing_data['website'].split()
        return urls

    @property
    def profile_pic_link(self):
        return None

    @property
    def popularity(self):
        return self.backing_data['likes']
