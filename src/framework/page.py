"""
Defines structures used to hold data that is being transmitted between modules and handlers.
"""

__author__ = 'justusadam'


class Component:

    _content = None

    def __init__(self, title, content=None, stylesheets=set(), metatags=set(), scripts=set()):
        self.content = content
        self._stylesheets = stylesheets
        self._metatags = metatags
        self._scripts = scripts
        self.title = title

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if not value:
            self._content = []
        elif isinstance(value, (tuple, set)):
            self._content = list(value)
        elif isinstance(value, list):
            self._content = value
        else:
            self._content = [value, ]

    @property
    def stylesheets(self):
        return self._stylesheets

    @stylesheets.setter
    def stylesheets(self, val):
        if isinstance(val, set):
            self._stylesheets = val
        elif isinstance(val, (list, tuple)):
            self._stylesheets = set(val)
        elif isinstance(val, str):
            self._stylesheets = {val}

    @property
    def metatags(self):
        return self._metatags

    @metatags.setter
    def metatags(self, val):
        if isinstance(val, set):
            self._metatags = val
        elif isinstance(val, (list, tuple)):
            self._metatags = set(val)
        elif isinstance(val, str):
            self._metatags = {val}

    @property
    def scripts(self):
        return self._scripts

    @scripts.setter
    def scripts(self, val):
        if isinstance(val, set):
            self._scripts = val
        elif isinstance(val, (list, tuple)):
            self._scripts = set(val)
        elif isinstance(val, str):
            self._scripts = {val}

    def __add__(self, other):
        self._stylesheets |= other.stylesheets
        self._metatags |= other.metatags
        self._scripts |= other.scripts
        self.content.append(other.content)
        return self


class Page(Component):
    def __init__(self, url, title='', content=None, stylesheets=set(), metatags=set(), scripts=set(), show_title=True):
        super().__init__(title, content, stylesheets, metatags, scripts)
        self._url = url
        self.show_title = show_title
        self.used_theme = 'active'