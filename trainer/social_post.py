import abc
import time
from email.utils import parsedate


class PostBase(object):
    """Represents a generic post on a social network."""
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def content(self):
        return 'Content'

    @abc.abstractproperty
    def time_posted(self):
        return int(time.time())

    @abc.abstractproperty
    def id(self):
        return 'Post ID'


class TwitterPost(PostBase):
    """Represents a post on Twitter."""

    def __init__(self, raw_post):
        self._content = raw_post['text']
        self._id = raw_post['id_str']
        self._time_posted = int(time.mktime(parsedate(raw_post['created_at'])))

    @property
    def content(self):
        return self._content

    @property
    def id(self):
        return self._id

    @property
    def time_posted(self):
        return self._time_posted


class FacebookPost(PostBase):
    """Represents a post on Facebook."""

    def __init__(self, raw_post):
        content_key = 'message' if 'message' in raw_post else 'description'
        self._content = raw_post[content_key]
        self._id = raw_post['id']
        self._time_posted = int(time.mktime(time.strptime(
                                raw_post['created_time'],
                                '%Y-%m-%dT%H:%M:%S+0000')))

    @property
    def content(self):
        return self._content

    @property
    def id(self):
        return self._id

    @property
    def time_posted(self):
        return self._time_posted
