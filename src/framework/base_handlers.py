"""
This file implements the basis for important default handler types.

It used to describe more functionality but has been refactored to be simpler and cleaner.

What remains are base classes that may be altered in the future but currently only serve as a launching point.

Eventually basic functions that the core demands these classes to implement may be added as empty functions
"""
from http import cookies
import sys
from urllib.error import HTTPError
from framework.url_tools import Url


__author__ = 'justusadam'


class ObjectHandler:
    def __init__(self, url):
        assert isinstance(url, Url)
        self._url = url
        self._headers = set()
        self._cookies = None

    def add_header(self, key, value):
        assert isinstance(key, str)
        assert isinstance(value, str)
        self._headers.add((key, value))

    def add_morsel(self, cookie):
        if not self._cookies:
            self._cookies = cookies.SimpleCookie()
        assert isinstance(cookie, (str, dict, cookies.Morsel))
        self._cookies.load(cookie)

    @property
    def compiled(self):
        return ''

    @property
    def headers(self):
        if self._cookies:
            # since rendering cookie values with the cookie object returns a string we split it again
            # to get header and value
            name, value = self._cookies.output().split(':', 1)
            # and remove redundant space at the beginning of the value string
            value = value[1:]
            self.add_header(name, value)
        return self._headers


class PageHandler(ObjectHandler):

    def __init__(self, url):
        super().__init__(url)
        self.page_type = None
        self.content_type = 'text/html'
        self.encoding = sys.getfilesystemencoding()

    @property
    def encoded(self):
        return self.compiled.encode(self.encoding)


class FieldHandler:

    @property
    def compiled(self):
        return ''


class ContentHandler(ObjectHandler):
    def __init__(self, url):
        super().__init__(url)

    def process_queries(self):
        if self.has_url_query():
            self.process_url_query()
        if self.is_post():
            self.process_post_query()

    def process_content(self):
        pass

    def has_url_query(self):
        return bool(self._url.get_query)

    def is_post(self):
        return bool(self._url.post_query)

    def process_url_query(self):
        pass

    def process_post_query(self):
        pass

    @property
    def compiled(self):
        self.process_queries()
        return self.process_content()


class RedirectMixIn(ObjectHandler):

    def redirect(self, destination=None):
        if 'destination' in self._url.get_query:
            destination = self._url.get_query['destination'][0]
        elif not destination:
            destination = str(self._url.path.prt_to_str(0, -1))
        raise HTTPError(str(self._url), 302, 'Redirect', [('Location', destination), ('Connection', 'close')], None)