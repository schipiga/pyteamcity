# -*- coding: utf-8 -*-

__author__ = "chipiga86@gmail.com"

from requests import Session
from xml.dom import minidom

class TeamCity(object):
    """TeamCity API
    """

    def __init__(self, url, username=None, password=None, guest=False):
        self._url = url.strip('/')
        self._session = Session()
        self._guest = guest
        if not guest:
            self._username = username
            self._password = password
            self._session.auth = (username, password)

    def __getattr__(self, name):
        return ApiChunk(self, name)

    @property
    def session(self):
        return self._session

    @property
    def url(self):
        return self._url

    @property
    def guest(self):
        return self._guest


class ApiChunk(object):

    def __init__(self, teamcity, method_name):
        self._teamcity = teamcity
        self._uri = teamcity.url
        if not teamcity.guest:
            self._expand_uri('httpAuth')
        self._expand_uri(method_name)

    def __call__(self, sep='/', **kwgs):
        if kwgs:
            if sep not in ('/', '?', '#'):
                raise RuntimeError('Invalid separator.')

            query = ('' if sep == '/' else sep) + '&'.join('%s=%s' % (key, val))
            self._expand_uri(query)
            return self

        else:
            params = {}
            if self._teamcity.guest:
                params = {'guest': 1}

            response = self._teamcity.session.get(self._uri, params=params)
            response.to_xml = lambda: minidom.parseString(response.text)

            return response

    def __getattr__(self, name):
            self._expand_uri(name)
            return self

    def _expand_uri(self, uri_chunk):
        self._uri = '%s/%s' % (self._uri, uri_chunk)
