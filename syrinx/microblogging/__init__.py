# -*- coding: utf-8 -*-
# Copyright 2007 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Based on python-twitter, a Idan Gazit fork of the python-twitter API by
# deWitt Clinton.
# https://github.com/idangazit/python-twitter

"""A library that provides a python interface to twitter-compatible APIs."""

__author__ = 'dewitt@google.com'
__version__ = '0.6.1-devel'


def get_version():
    return __version__


def get_author():
    return __author__


import base64
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5
import os
import simplejson
import sys
import tempfile
import time
import calendar
import urllib
import urllib2
from urlparse import urlparse, urlunparse


class Error(Exception):
    """Base class for errors."""

    pass


class Status(object):
    """A class representing the Status structure used by the API.

    The Status structure exposes the following properties:

        status.created_at
        status.created_at_in_seconds  # read only
        status.favorited
        status.id
        status.text
        status.relative_created_at  # read only
        status.user

    """

    def __init__(self, created_at=None, favorited=None, id=None, text=None,
                 user=None, now=None):
        """An object to hold a status message.

        This class is normally instantiated by the microblogging.API class and
        returned in a sequence.

        Note: Dates are posted in the form "Sat Jan 27 04:17:38 +0000 2007".

        Args:
            created_at:
                The time this status message was posted.
            favorited:
                Whether this is a favorite of the authenticated user.
            id:
                The unique id of this status message.
            text:
                The text of this status message.
            relative_created_at:
                A human readable string representing the posting time.
            user:
                A microblogging.User instance representing the person posting
                the message.
            now:
                The current time, if the client choses to set it.  Defaults to
                the wall clock time.

        """
        self.created_at = created_at
        self.favorited = favorited
        self.id = id
        self.text = text
        self.user = user
        self.now = now

    @property
    def created_at_in_seconds(self):
        """The time this status message was posted, in seconds since the
        epoch."""
        return calendar.timegm(
            time.strptime(self.created_at, '%a %b %d %H:%M:%S +0000 %Y'))

    @property
    def relative_created_at(self):
        """Human redable string representing the posting time.

        Returns:
            A human readable string representing the posting time

        """
        fudge = 1.25
        delta = int(self.now) - int(self.created_at_in_seconds)

        if delta < (1 * fudge):
            return 'about a second ago'
        elif delta < (60 * (1 / fudge)):
            return 'about %d seconds ago' % (delta)
        elif delta < (60 * fudge):
            return 'about a minute ago'
        elif delta < (60 * 60 * (1 / fudge)):
            return 'about %d minutes ago' % (delta / 60)
        elif delta < (60 * 60 * fudge):
            return 'about an hour ago'
        elif delta < (60 * 60 * 24 * (1 / fudge)):
            return 'about %d hours ago' % (delta / (60 * 60))
        elif delta < (60 * 60 * 24 * fudge):
            return 'about a day ago'
        else:
            return 'about %d days ago' % (delta / (60 * 60 * 24))

    @property
    def now(self):
        """Wallclock time for this status message.

        Used to calculate relative_created_at.  Defaults to the time the object
        was instantiated.

        Returns:
            Whatever the status instance believes the current time to be, in
            seconds since the epoch.

        """
        if self._now is None:
            self._now = time.time()
        return self._now

    @now.setter
    def now(self, now):
        """Set the wallclock time for this status message.

        Used to calculate relative_created_at.  Defaults to the time the object
        was instantiated.

        Args:
            now:
                The wallclock time for this instance.

        """
        self._now = now

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        try:
            return other and \
                self.created_at == other.created_at and \
                self.id == other.id and \
                self.text == other.text and \
                self.user == other.user
        except AttributeError:
            return False

    def __str__(self):
        """A string representation of this microblogging.Status instance.

        The return value is the same as the JSON string representation.

        Returns:
            A string representation of this microblogging.Status instance.

        """
        return self.as_json()

    def as_json(self):
        """A JSON representation of this microblogging.Status instance.

        Returns:
            A JSON string representation of this microblogging.Status instance

        """
        return simplejson.dumps(self.as_dict(), sort_keys=True)

    def as_dict(self):
        """A dict representation of this microblogging.Status instance.

        The return value uses the same key names as the JSON representation.

        Return:
            A dict representing this microblogging.Status instance

        """
        data = {}
        if self.created_at:
            data['created_at'] = self.created_at
        if self.favorited:
            data['favorited'] = self.favorited
        if self.id:
            data['id'] = self.id
        if self.text:
            data['text'] = self.text
        if self.user:
            data['user'] = self.user.as_dict()
        return data

    @staticmethod
    def get_from_json(data):
        """Create a new instance based on a JSON dict.

        Args:
            data:
                A JSON dict, as converted from the JSON in the twitter API.
        Returns:
            A microblogging.Status instance.
        """
        if 'user' in data:
            user = User.get_from_json(data['user'])
        else:
            user = None
        return Status(created_at=data.get('created_at', None),
            favorited=data.get('favorited', None), id=data.get('id', None),
            text=data.get('text', None), user=user)


class User(object):
    """A class representing the User structure used by the twitter API.

    The User structure exposes the following properties:

        user.id
        user.name
        user.screen_name
        user.location
        user.description
        user.profile_image_url
        user.url
        user.status
    """
    def __init__(self, id=None, name=None, screen_name=None, location=None,
                 description=None, profile_image_url=None, url=None,
                 status=None):
        self.id = id
        self.name = name
        self.screen_name = screen_name
        self.location = location
        self.description = description
        self.profile_image_url = profile_image_url
        self.url = url
        self.status = status

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        try:
            return other and \
                self.id == other.id and \
                self.name == other.name and \
                self.screen_name == other.screen_name and \
                self.location == other.location and \
                self.description == other.description and \
                self.profile_image_url == other.profile_image_url and \
                self.url == other.url and \
                self.status == other.status
        except AttributeError:
            return False

    def __str__(self):
        """A string representation of this microblogging.User instance.

        The return value is the same as the JSON string representation.

        Returns:
            A string representation of this microblogging.User instance.
        """
        return self.as_json()

    def as_json(self):
        """A JSON string representation of this microblogging.User instance.

        Returns:
            A JSON string representation of this microblogging.User instance
        """
        return simplejson.dumps(self.as_dict(), sort_keys=True)

    def as_dict(self):
        """A dict representation of this microblogging.User instance.

        The return value uses the same key names as the JSON representation.

        Return:
            A dict representing this microblogging.User instance
        """
        data = {}
        if self.id:
            data['id'] = self.id
        if self.name:
            data['name'] = self.name
        if self.screen_name:
            data['screen_name'] = self.screen_name
        if self.location:
            data['location'] = self.location
        if self.description:
            data['description'] = self.description
        if self.profile_image_url:
            data['profile_image_url'] = self.profile_image_url
        if self.url:
            data['url'] = self.url
        if self.status:
            data['status'] = self.status.as_dict()
        return data

    @staticmethod
    def get_from_json(data):
        """Create a new instance based on a JSON dict.

        Args:
            data:
                A JSON dict, as converted from the JSON in the twitter API.
        Returns:
            A microblogging.User instance
        """
        if 'status' in data:
            status = Status.get_from_json(data['status'])
        else:
            status = None
        return User(id=data.get('id', None), name=data.get('name', None),
            screen_name=data.get('screen_name', None),
            location=data.get('location', None),
            description=data.get('description', None),
            profile_image_url=data.get('profile_image_url', None),
            url=data.get('url', None), status=status)


class DirectMessage(object):
    """A class representing the DirectMessage structure used by the twitter
    API.

    The DirectMessage structure exposes the following properties:

        direct_message.id
        direct_message.created_at
        direct_message.created_at_in_seconds # read only
        direct_message.sender_id
        direct_message.sender_screen_name
        direct_message.recipient_id
        direct_message.recipient_screen_name
        direct_message.text
    """

    def __init__(self, id=None, created_at=None, sender_id=None,
                 sender_screen_name=None, recipient_id=None,
                 recipient_screen_name=None, text=None):
        """An object to hold a Twitter direct message.

        This class is normally instantiated by the microblogging.API class and
        returned in a sequence.

        Note: Dates are posted in the form "Sat Jan 27 04:17:38 +0000 2007".

        Args:
            id:
                The unique id of this direct message.
            created_at:
                The time this direct message was posted.
            sender_id:
                The id of the twitter user that sent this message.
            sender_screen_name:
                The name of the twitter user that sent this message.
            recipient_id:
                The id of the twitter that received this message.
            recipient_screen_name:
                The name of the twitter that received this message.
            text:
                The text of this direct message.
        """
        self.id = id
        self.created_at = created_at
        self.sender_id = sender_id
        self.sender_screen_name = sender_screen_name
        self.recipient_id = recipient_id
        self.recipient_screen_name = recipient_screen_name
        self.text = text

    @property
    def created_at_in_seconds(self):
        """The time this direct message was posted, in seconds since the epoch.

        Returns:
            The time this direct message was posted, in seconds since the
            epoch.
        """
        return calendar.timegm(
            time.strptime(self.created_at, '%a %b %d %H:%M:%S +0000 %Y'))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        try:
            return other and \
                self.id == other.id and \
                self.created_at == other.created_at and \
                self.sender_id == other.sender_id and \
                self.sender_screen_name == other.sender_screen_name and \
                self.recipient_id == other.recipient_id and \
                self.recipient_screen_name == other.recipient_screen_name and \
                self.text == other.text
        except AttributeError:
            return False

    def __str__(self):
        """A string representation of this microblogging.DirectMessage
        instance.

        The return value is the same as the JSON string representation.

        Returns:
            A string representation of this microblogging.DirectMessage
            instance.
        """
        return self.as_json()

    def as_json(self):
        """A JSON string representation of this microblogging.DirectMessage
        instance.

        Returns:
            A JSON string representation of this microblogging.DirectMessage
            instance.
        """
        return simplejson.dumps(self.as_dict(), sort_keys=True)

    def as_dict(self):
        """A dict representation of this microblogging.DirectMessage instance.

        The return value uses the same key names as the JSON representation.

        Return:
            A dict representing this microblogging.DirectMessage instance
        """
        data = {}
        if self.id:
            data['id'] = self.id
        if self.created_at:
            data['created_at'] = self.created_at
        if self.sender_id:
            data['sender_id'] = self.sender_id
        if self.sender_screen_name:
            data['sender_screen_name'] = self.sender_screen_name
        if self.recipient_id:
            data['recipient_id'] = self.recipient_id
        if self.recipient_screen_name:
            data['recipient_screen_name'] = self.recipient_screen_name
        if self.text:
            data['text'] = self.text
        return data

    @staticmethod
    def get_from_json(data):
        """Create a new instance based on a JSON dict.

        Args:
            data:
                A JSON dict, as converted from the JSON in the twitter API.
        Returns:
            A microblogging.DirectMessage instance.
        """
        return DirectMessage(created_at=data.get('created_at', None),
            recipient_id=data.get('recipient_id', None),
            sender_id=data.get('sender_id', None), text=data.get('text', None),
            sender_screen_name=data.get('sender_screen_name', None),
            id=data.get('id', None),
            recipient_screen_name=data.get('recipient_screen_name', None))


class API(object):
    """A python interface to twitter-compatible APIs.

    By default, the API caches results for 1 minute.

    Example usage.  To create an instance of the microblogging.API class, with
    no authentication:

        >>> import twitter
        >>> api = microblogging.API()

    To fetch the most recently posted public twitter status messages:

        >>> statuses = api.public_timeline()
        >>> print [s.user.name for s in statuses]
        [u'DeWitt', u'Kesuke Miyagi', u'ev', u'Buzz Andersen']  # ...

    To fetch a single user's public status messages, where "user" is either a
    Twitter "short name" or their user id.

        >>> statuses = api.user_timeline(user)
        >>> print [s.text for s in statuses]

    To use authentication, instantiate the microblogging.API class with a
    username and password:

        >>> api = microblogging.API(username='user', password=u'passwd123')

    To fetch your friends (after being authenticated):

        >>> users = api.friends()
        >>> print [u.name for u in users]

    To post a twitter status message (after being authenticated):

        >>> status = api.post('I love python-twitter!')
        >>> print status.text
        I love python-twitter!

    There are many other methods, including:

        >>> api.post_direct_message(user, text)
        >>> api.user(user)
        >>> api.replies()
        >>> api.user_timeline(user)
        >>> api.status(id)
        >>> api.destroy_status(id)
        >>> api.friends_timeline(user)
        >>> api.friends(user)
        >>> api.followers()
        >>> api.featured()
        >>> api.direct_messages()
        >>> api.post_direct_message(user, text)
        >>> api.destroy_direct_message(id)
        >>> api.destroy_friendship(user)
        >>> api.create_friendship(user)

    """

    DEFAULT_CACHE_TIMEOUT = 60  # 1 minute

    _API_REALM = 'Microblogging API'

    def __init__(self, username=None, password=None, use_ssl=True, domain=None,
                 input_encoding=None, request_headers=None):
        """Instantiate a new microblogging.API object.

        Args:
            username:
                The username of the twitter account. [optional]
            password:
                The password for the twitter account. [optional]
            input_encoding:
                The encoding used to encode input strings. [optional]
            request_header:
                A dictionary of additional HTTP request headers. [optional]

        """
        self.use_ssl = use_ssl
        self.domain = domain
        self.cache = _FileCache()
        self.urllib = urllib2
        self.cache_timeout = API.DEFAULT_CACHE_TIMEOUT
        self._initialize_request_headers(request_headers)
        self._initialize_user_agent()
        self._initialize_default_parameters()
        self._input_encoding = input_encoding
        self.set_credentials(username, password)

    def public_timeline(self, since_id=None):
        """Fetch the sequnce of public microblogging.Status message for all
        users.

        Args:
            since_id:
                Returns only public statuses with an ID greater than (that is,
                more recent than) the specified ID. [Optional]
        Returns:
            An sequence of microblogging.Status instances, one for each
            message.

        """
        parameters = {}
        if since_id:
            parameters['since_id'] = since_id
        url = self.get_url('/statuses/public_timeline.json')
        json = self._fetch_url(url,  parameters=parameters)
        data = simplejson.loads(json)
        return [Status.get_from_json(x) for x in data]

    def friends_timeline(self, user=None, since=None, since_id=None):
        """Fetch the sequence of microblogging.Status messages for a user's
        friends.

        The microblogging.API instance must be authenticated if the user is
        private.

        Args:
            user:
                Specifies the ID or screen name of the user for whom to return
                the friends_timeline.  If unspecified, the username and
                password must be set in the microblogging.API instance.
                [optional]
            since:
                Narrows the returned results to just those statuses created
                after the specified HTTP-formatted date. [optional]
            since_id:
                Returns only statuses with an ID greater than (that is, more
                recent than) the specified ID. [optional]
        Returns:
            A sequence of microblogging.Status instances, one for each message.

        """
        if user:
            url = self.get_url('/statuses/friends_timeline/%s.json' % user)
        elif not user and not self._username:
            raise Error('User must be specified if API is not authenticated.')
        else:
            url = self.get_url('/statuses/friends_timeline.json')
        parameters = {}
        if since:
            parameters['since'] = since
        if since_id:
            parameters['since_id'] = since_id
        json = self._fetch_url(url, parameters=parameters)
        data = simplejson.loads(json)
        return [Status.get_from_json(x) for x in data]

    def user_timeline(self, user=None, count=None, since=None,
                      since_id=None):
        """Fetch the sequence of public microblogging.Status messages for a
        single user.

        The microblogging.API instance must be authenticated if the user is
        private.

        Args:
            user:
                Either the username (short_name) or id of the user to retrieve.
                If not specified, then the current authenticated user is used.
                [optional]
            count:
                The number of status messages to retrieve. [optional]
            since:
                Narrows the returned results to just those statuses created
                after the specified HTTP-formatted date. [optional]
            since_id:
                Returns only statuses with an ID greater than (that is, more
                recent than) the specified ID. [optional]
        Returns:
            A sequence of microblogging.Status instances, one for each message
            up to count.

        """
        try:
            if count:
                int(count)
        except:
            raise Error("Count must be an integer.")
        parameters = {}
        if count:
            parameters['count'] = count
        if since:
            parameters['since'] = since
        if since_id:
            parameters['since_id'] = since_id
        if user:
            url = self.get_url('/statuses/user_timeline/%s.json' % user)
        elif not user and not self._username:
            raise Error('User must be specified if API is not authenticated.')
        else:
            url = self.get_url('/statuses/user_timeline.json')
        json = self._fetch_url(url, parameters=parameters)
        data = simplejson.loads(json)
        return [Status.get_from_json(x) for x in data]

    def status(self, id):
        """Returns a single status message.

        The microblogging.API instance must be authenticated if the status
        message is private.

        Args:
            id:
                The numerical ID of the status you're trying to retrieve.
        Returns:
            A microblogging.Status instance representing that status message.

        """
        try:
            if id:
                int(id)
        except:
            raise Error("id must be an integer.")
        url = self.get_url('/statuses/show/%s.json' % id)
        json = self._fetch_url(url)
        data = simplejson.loads(json)
        return Status.get_from_json(data)

    def destroy_status(self, id):
        """Destroys the status specified by the required ID parameter.

        The microblogging.API instance must be authenticated and the
        authenticating user must be the author of the specified status.

        Args:
            id:
                The numerical ID of the status you're trying to destroy.
        Returns:
            A microblogging.Status instance representing the destroyed status
            message.

        """
        try:
            if id:
                int(id)
        except:
            raise Error("id must be an integer.")
        url = self.get_url('/statuses/destroy/%s.json' % id)
        json = self._fetch_url(url, post_data={})
        data = simplejson.loads(json)
        return Status.get_from_json(data)

    def post(self, text):
        """Post a twitter status message from the authenticated user.

        The microblogging.API instance must be authenticated.

        Args:
            text:
                The message text to be posted.  Must be less than 140
                characters.
        Returns:
            A microblogging.Status instance representing the message posted.

        """
        if not self._username:
            raise Error('The microblogging.API instance must be ' + \
                        'authenticated.')
        if len(text) > 140:
            raise Error('Text must be less than or equal to 140 characters.')
        url = self.get_url('/statuses/update.json')
        data = {'status': text}
        json = self._fetch_url(url, post_data=data)
        data = simplejson.loads(json)
        return Status.get_from_json(data)

    def replies(self):
        """Get a sequence of status messages representing the 20 most recent
        replies (status updates prefixed with @username) to the authenticating
        user.

        Returns:
            A sequence of microblogging.Status instances, one for each reply to
            the user.

        """
        url = self.get_url('/statuses/replies.json')
        if not self._username:
            raise Error('The microblogging.API instance must be ' + \
                        'authenticated.')
        json = self._fetch_url(url)
        data = simplejson.loads(json)
        return [Status.get_from_json(x) for x in data]

    def friends(self, user=None):
        """Fetch the sequence of microblogging.User instances, one for each
        friend.

        The microblogging.API instance must be authenticated.

        Args:
            user:
                The username or id of the user whose friends you are fetching.
                If not specified, defaults to the authenticated user.
                [optional]
        Returns:
            A sequence of microblogging.User instances, one for each friend.

        """
        if not self._username:
            raise Error('microblogging.API instance must be authenticated.')
        if user:
            url = self.get_url('/statuses/friends/%s.json' % user)
        else:
            url = self.get_url('/statuses/friends.json')
        json = self._fetch_url(url)
        data = simplejson.loads(json)
        return [User.get_from_json(x) for x in data]

    def followers(self):
        """Fetch the sequence of microblogging.User instances, one for each
        follower.

        The microblogging.API instance must be authenticated.

        Returns:
            A sequence of microblogging.User instances, one for each follower.

        """
        if not self._username:
            raise Error('microblogging.API instance must be authenticated.')
        url = self.get_url('/statuses/followers.json')
        json = self._fetch_url(url)
        data = simplejson.loads(json)
        return [User.get_from_json(x) for x in data]

    def featured(self):
        """Fetch the sequence of featured microblogging.User instances on
        server.

        The microblogging.API instance must be authenticated.

        Returns:
            A sequence of microblogging.User instances.

        """
        url = self.get_url('/statuses/featured.json')
        json = self._fetch_url(url)
        data = simplejson.loads(json)
        return [User.get_from_json(x) for x in data]

    def user(self, user):
        """Returns a single user.

        The microblogging.API instance must be authenticated.

        Args:
            user:
                The username or id of the user to retrieve.

        Returns:
            A microblogging.User instance representing that user.

        """
        url = self.get_url('/users/show/%s.json' % user)
        json = self._fetch_url(url)
        data = simplejson.loads(json)
        return User.get_from_json(data)

    def direct_messages(self, since=None):
        """Returns a list of the direct messages sent to the authenticating
        user.

        The microblogging.API instance must be authenticated.

        Args:
            since:
                Narrows the returned results to just those statuses created
                after the specified HTTP-formatted date. [optional]
        Returns:
            A sequence of microblogging.DirectMessage instances.

        """
        url = self.get_url('/direct_messages.json')
        if not self._username:
            raise Error('The microblogging.API instance must be ' + \
                        'authenticated.')
        parameters = {}
        if since:
            parameters['since'] = since
        json = self._fetch_url(url, parameters=parameters)
        data = simplejson.loads(json)
        return [DirectMessage.get_from_json(x) for x in data]

    def post_direct_message(self, user, text):
        """Post a twitter direct message from the authenticated user.

        The microblogging.API instance must be authenticated.

        Args:
            user:
                The ID or screen name of the recipient user.
            text:
                The message text to be posted.  Must be less than 140
                characters.
        Returns:
            A microblogging.DirectMessage instance representing the message
            posted.

        """
        if not self._username:
            raise Error('The microblogging.API instance must be ' + \
                        'authenticated.')
        url = self.get_url('/direct_messages/new.json')
        data = {'text': text, 'user': user}
        json = self._fetch_url(url, post_data=data)
        data = simplejson.loads(json)
        return DirectMessage.get_from_json(data)

    def destroy_direct_message(self, id):
        """Destroys the direct message specified in the required ID parameter.

        The microblogging.API instance must be authenticated, and the
        authenticating user must be the recipient of the specified direct
        message.

        Args:
            id:
                The id of the direct message to be destroyed
        Returns:
            A microblogging.DirectMessage instance representing the message
            destroyed.

        """
        url = self.get_url('/direct_messages/destroy/%s.json' % id)
        json = self._fetch_url(url, post_data={})
        data = simplejson.loads(json)
        return DirectMessage.get_from_json(data)

    def create_friendship(self, user):
        """Befriends the user specified in the user parameter as the
        authenticating user.

        The microblogging.API instance must be authenticated.

        Args:
            user:
                The ID or screen name of the user to befriend.
        Returns:
            A microblogging.User instance representing the befriended user.

        """
        url = self.get_url('/friendships/create/%s.json' % user)
        json = self._fetch_url(url, post_data={})
        data = simplejson.loads(json)
        return User.get_from_json(data)

    def destroy_friendship(self, user):
        """Discontinues friendship with the user specified in the user
        parameter.

        The microblogging.API instance must be authenticated.

        Args:
            user:
                The ID or screen name of the user  with whom to discontinue
                friendship.
        Returns:
            A microblogging.User instance representing the discontinued friend.

        """
        url = self.get_url('/friendships/destroy/%s.json' % user)
        json = self._fetch_url(url, post_data={})
        data = simplejson.loads(json)
        return User.get_from_json(data)

    def create_favorite(self, status):
        """Favorites the status specified in the status parameter as the
        authenticating user.

        Returns the favorite status when successful.

        The microblogging.API instance must be authenticated.

        Args:
            status:
                The microblogging.Status instance to mark as a favorite.
        Returns:
            A microblogging.Status instance representing the newly-marked
            favorite.

        """
        url = self.get_url('/favorites/create/%s.json' % status.id)
        json = self._fetch_url(url, post_data={})
        data = simplejson.loads(json)
        return Status.get_from_json(data)

    def destroy_favorite(self, status):
        """Un-favorites the status specified in the ID parameter as the
        authenticating user.

        Returns the un-favorited status in the requested format when
        successful.

        The microblogging.API instance must be authenticated.

        Args:
            status:
                The microblogging.Status to unmark as a favorite.
        Returns:
            A microblogging.Status instance representing the newly-unmarked
            favorite.

        """
        url = self.get_url('/favorites/destroy/%s.json' % status.id)
        json = self._fetch_url(url, post_data={})
        data = simplejson.loads(json)
        return Status.get_from_json(data)

    def set_credentials(self, username, password):
        """Set the username and password for this instance.

        Args:
            username:
                The twitter username.
            password:
                The twitter password.

        """
        self._username = username
        self._password = password

    def clear_credentials(self):
        """Clear the username and password for this instance."""
        self._username = None
        self._password = None

    @property
    def user_agent(self):
        """User agent."""
        if 'User-Agent' in self._request_headers:
            return self._request_headers['User-Agent']
        return ''

    @user_agent.setter
    def user_agent(self, user_agent):
        """Override the default user agent.

        Args:
            user_agent:
                A string that should be send to the server as the User-agent.

        """
        self._request_headers['User-Agent'] = user_agent

    # FIXME: Remove this from here.
    def SetXTwitterHeaders(self, client, url, version):
        """Set the X-Twitter HTTP headers that will be sent to the server.

        Args:
            client:
                The client name as a string.  Will be sent to the server as the
                'X-Twitter-Client' header.
            url:
                The URL of the meta.xml as a string.  Will be sent to the
                server as the 'X-Twitter-Client-URL' header.
            version:
                The client version as a string.  Will be sent to the server as
                the 'X-Twitter-Client-Version' header.

        """
        self._request_headers['X-Twitter-Client'] = client
        self._request_headers['X-Twitter-Client-URL'] = url
        self._request_headers['X-Twitter-Client-Version'] = version

    @property
    def source(self):
        """The source of the message."""
        if 'source' in self._default_params:
            return self._default_params['source']

    @source.setter
    def source(self, source):
        """Suggest the "from source" value to be displayed on the Twitter web
        site.

        The value of the 'source' parameter must be first recognized by the
        Twitter server.  New source values are authorized on a case by case
        basis by the Twitter development team.

        Args:
            source:
                The source name as a string.  Will be sent to the server as the
                'source' parameter.

        """
        self._default_params['source'] = source

    def _build_url(self, url, path_elements=None, extra_params=None):
        # Break url into consituent parts.
        (scheme, netloc, path, params, query, fragment) = urlparse(url)

        # Add any additional path elements to the path
        if path_elements:
            # Filter out the path elements that have a value of None
            p = [i for i in path_elements if i]
            if not path.endswith('/'):
                path += '/'
            path += '/'.join(p)

        # Add any additional query parameters to the query string
        if extra_params and len(extra_params) > 0:
            extra_query = self._encode_parameters(extra_params)
            # Add it to the existing query
            if query:
                query += '&' + extra_query
            else:
                query = extra_query

        # Return the rebuilt URL
        return urlunparse((scheme, netloc, path, params, query,
            fragment))

    def _initialize_request_headers(self, request_headers):
        if request_headers:
            self._request_headers = request_headers
        else:
            self._request_headers = {}

    def _initialize_user_agent(self):
        user_agent = 'Python-urllib/%s (python-microbloggin/%s)' % (
            self.urllib.__version__, get_version())  # TODO: Chequear.
        self.user_agent = user_agent

    def _initialize_default_parameters(self):
        self._default_params = {}

    def _add_authorization_header(self, username, password):
        if username and password:
            basic_auth = base64.encodestring('%s:%s' % (
                username, password))[:-1]
            self._request_headers['Authorization'] = 'Basic %s' % basic_auth

    def _remove_authorization_header(self):
        if self._request_headers and 'Authorization' in self._request_headers:
            del self._request_headers['Authorization']

    def _get_opener(self, url, username=None, password=None):
        if username and password:
            self._add_authorization_header(username, password)
            handler = self.urllib.HTTPBasicAuthHandler()
            (scheme, netloc, path, params, query, fragment) = urlparse(url)
            handler.add_password(API._API_REALM, netloc, username, password)
            opener = self.urllib.build_opener(handler)
        else:
            opener = self.urllib.build_opener()
        opener.addheaders = self._request_headers.items()
        return opener

    def _encode(self, s):
        if self._input_encoding:
            return unicode(s, self._input_encoding).encode('utf-8')
        else:
            return unicode(s).encode('utf-8')

    def _encode_parameters(self, parameters):
        """Return a string in key=value&key=value form.

        Values of None are not included in the output string.

        Args:
            parameters:
                A dict of (key, value) tuples, where value is encoded as
                specified by self._encoding.
        Returns:
            A URL-encoded string in "key=value&key=value" form.
        """
        if parameters is None:
            return None
        else:
            return urllib.urlencode(dict(
                [(k, self._encode(v))
                    for k, v in parameters.items() if v is not None]))

    def _encode_post_data(self, post_data):
        """Return a string in key=value&key=value form.

        Values are assumed to be encoded in the format specified by
        self._encoding, and are subsequently URL encoded.

        Args:
            post_data:
                A dict of (key, value) tuples, where value is encoded as
                specified by self._encoding.
        Returns:
            A URL-encoded string in "key=value&key=value" form.
        """
        if post_data is None:
            return None
        else:
            return urllib.urlencode(dict(
                [(k, self._encode(v)) for k, v in post_data.items()]))

    def get_url(self, url):
        """Retrieves the full URL including the domain."""
        protocol = 'http'
        if self.use_ssl:
            protocol += 's'
        return '%s://%s%s' % (protocol, self.domain, url)

    def _fetch_url(self, url, post_data=None, parameters=None, no_cache=None):
        """Fetch a URL, optionally caching for a specified time.

        Args:
            url:
                The URL to retrieve
            post_data:
                A dict of (str, unicode) key value pairs.  If set, POST will be
                used.
            parameters:
                A dict of key/value pairs that should added to the query
                string. [OPTIONAL]
            no_cache:
                If true, overrides the cache on the current request.
        Returns:
            A string containing the body of the response.
        """
        # Build the extra parameters dict.
        extra_params = {}
        if self._default_params:
            extra_params.update(self._default_params)
        if parameters:
            extra_params.update(parameters)

        # Add key/value parameters to the query string of the url.
        url = self._build_url(url, extra_params=extra_params)

        # Get a url opener that can handle basic auth.
        opener = self._get_opener(url, username=self._username,
            password=self._password)

        encoded_post_data = self._encode_post_data(post_data)

        # Open and return the URL immediately if we're not going to cache.
        if encoded_post_data or no_cache or not self.cache or \
                not self.cache_timeout:
            url_data = opener.open(url, encoded_post_data).read()
        else:
            # Unique keys are a combination of the url and the username.
            if self._username:
                key = self._username + ':' + url
            else:
                key = url

            # See if it has been cached before.
            last_cached = self.cache.get_cached_time(key)

            # If the cached version is outdated then fetch and store another.
            now = time.time()
            if not last_cached or now >= last_cached + self.cache_timeout:
                url_data = opener.open(url, encoded_post_data).read()
                self.cache.set(key, url_data)
            else:
                url_data = self.cache.get(key)

        # Always return the latest version.
        return url_data


class _FileCacheError(Exception):
    """Base exception class for FileCache related errors"""

    pass


class _FileCache(object):

    DEPTH = 3

    def __init__(self, root_directory=None):
        self._initialize_root_directory(root_directory)

    def get(self, key):
        path = self._get_path(key)
        if os.path.exists(path):
            return open(path).read()
        else:
            return None

    def set(self, key, data):
        path = self._get_path(key)
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.isdir(directory):
            raise _FileCacheError('%s exists but is not a directory.' % (
                directory,))
        temp_fd, temp_path = tempfile.mkstemp()
        temp_fp = os.fdopen(temp_fd, 'w')
        temp_fp.write(data)
        temp_fp.close()
        if not path.startswith(self._root_directory):
            raise _FileCacheError('%s does not appear to live under %s' % (
                path, self._root_directory))
        if os.path.exists(path):
            os.remove(path)
        os.rename(temp_path, path)

    def remove(self, key):
        path = self._get_path(key)
        if not path.startswith(self._root_directory):
            raise _FileCacheError('%s does not appear to live under %s' % (
                path, self._root_directory))
        if os.path.exists(path):
            os.remove(path)

    def get_cached_time(self, key):
        path = self._get_path(key)
        if os.path.exists(path):
            return os.path.getmtime(path)
        else:
            return None

    def _username(self):
        """Attempt to find the username in a cross-platform fashion."""
        try:
            return os.getenv('USER') or \
                os.getenv('LOGNAME') or \
                os.getenv('USERNAME') or \
                os.getlogin() or \
                'nobody'
        except (IOError, OSError), e:
            return 'nobody'

    def _get_tmp_cache_path(self):
        username = self._username()
        cache_directory = 'python.cache_' + username
        return os.path.join(tempfile.gettempdir(), cache_directory)

    def _initialize_root_directory(self, root_directory):
        if not root_directory:
            root_directory = self._get_tmp_cache_path()
            root_directory = os.path.abspath(root_directory)
        if not os.path.exists(root_directory):
            os.mkdir(root_directory)
        if not os.path.isdir(root_directory):
            raise _FileCacheError('%s exists but is not a directory.' % (
                root_directory,))
        self._root_directory = root_directory

    def _get_path(self, key):
        hashed_key = md5(key).hexdigest()
        return os.path.join(
            self._root_directory, self._get_prefix(hashed_key), hashed_key)

    def _get_prefix(self, hashed_key):
        return os.path.sep.join(hashed_key[0:_FileCache.DEPTH])
