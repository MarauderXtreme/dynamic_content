import pathlib
import re
import sys

from dyc.dchttp import response
from dyc.util import html, decorators, config
from dyc import core


__author__ = 'justusadam'

VAR_REGEX = re.compile("\{([\w_-]*?)\}")

ARG_REGEX = re.compile(":(\w+?):(\w*)")

_defaults = {
    'theme': 'default_theme',
    'view': 'page',
    'content_type': 'text/html',
    'encoding': sys.getfilesystemencoding()
}


@core.Component('TemplateFormatter')
class TemplateFormatter:

    responses = {
        None: 'serve_document',
        'redirect': 'redirect'
    }

    @decorators.multicache
    def theme_config(self, theme):
        return config.read_config('themes/' + theme + '/config.json')

    def __call__(self, view_name, model, url):

        c = ARG_REGEX.match(view_name) if view_name else None

        c, *arg = c.groups() if c else (None, view_name)

        handler = getattr(self, self.responses[c])

        code, document, headers = handler(model, url, *arg)

        r = response.Response(document, code, headers, model.cookies)
        for attr in ['content_type', 'encoding']:
            setattr(r, attr, getattr(model, attr) if hasattr(model, attr) else _defaults[attr])
        return r


    def serve_document(self, model, url, view_name):
        theme = model.theme if model.theme else _defaults['theme']
        encoding = model.encoding if hasattr(model, 'encoding') and model.encoding else _defaults['encoding']

        if 'no-encode' in model.decorator_attributes:
            document = model['content']

        elif 'no_view' in model.decorator_attributes or view_name is None:
            document = model['content'].encode(encoding)
        else:
            pairing = self.initial_pairing(model, theme, url)
            file = open(self.view_path(theme, view_name)).read()
            for a in VAR_REGEX.finditer(file):
                if a.group(1) not in pairing:
                    pairing.__setitem__(a.group(1), '')
            document = file.format(**{a: str(pairing[a]) for a in pairing})
            document = document.encode(encoding)

        return 200, document, model.headers

    @staticmethod
    def view_path(theme, view):
        return '/'.join(['themes', theme, 'template', view + '.html'])

    def redirect(self, model, url, attr):
        if not attr:
            attr = '/'
        headers = model.headers.copy()
        headers.add(("Location", attr))
        return 301, None, headers

    @staticmethod
    def theme_path_alias(theme):
        return '/theme/' + theme

    def _get_my_folder(self):
        return str(pathlib.Path(sys.modules[self.__class__.__module__].__file__).parent)

    def _get_config_folder(self):
        return self._get_my_folder()

    def compile_stylesheets(self, model, theme):
        theme_config = self.theme_config(theme)
        s = self._list_from_model(model, 'stylesheets')
        if 'stylesheets' in theme_config:
            s += list(html.Stylesheet(
                self.theme_path_alias(theme) + '/' + theme_config['stylesheet_directory'] + '/' + a) for
                      a
                      in theme_config['stylesheets'])
        return ''.join([str(a) for a in s])

    @staticmethod
    def _list_from_model(model,  ident):
        if ident in model:
            return model[ident]
        else:
            return []

    def compile_scripts(self, model, theme):
        theme_config = self.theme_config(theme)
        s = self._list_from_model(model, 'scripts')
        if 'scripts' in theme_config:
            s += list(
                html.Script(self.theme_path_alias(theme) + '/' + theme_config['script_directory'] + '/' + a) for
                a
                in theme_config['scripts'])
        return ''.join([str(a) for a in s])

    def compile_meta(self, model, theme):
        theme_config = self.theme_config(theme)
        if 'favicon' in theme_config:
            favicon = theme_config['favicon']
        else:
            favicon = 'favicon.icon'
        return str(
            html.LinkElement('/theme/' + theme + '/' + favicon, rel='shortcut icon', element_type='image/png'))

    def initial_pairing(self, model, theme, url) -> dict:
        a = model.copy()
        a.update({
            'scripts': self.compile_scripts(model, theme),
            'stylesheets': self.compile_stylesheets(model, theme),
            'meta': self.compile_meta(model, theme)
        })
        a.setdefault('breadcrumbs', self.render_breadcrumbs(url))
        a.setdefault('pagetitle',
                     html.A('/', 'dynamic_content - fast, python and extensible'))
        a.setdefault('footer', str(
            html.ContainerElement(
                html.ContainerElement('\'dynamic_content\' CMS - &copy; Justus Adam 2014', html_type='p'),
                element_id='powered_by', classes={'common', 'copyright'})))
        return a


    breadcrumb_separator = '>>'

    @staticmethod
    def breadcrumbs(url):
        path = url.path.split('/')
        yield 'home', '/'
        for i in range(1, len(path)):
            yield path[i], '/'.join(path[:i+1])

    def render_breadcrumbs(self, url):
        def acc():
            for (name, location) in self.breadcrumbs(url):
                for i in [
                    html.ContainerElement(self.breadcrumb_separator, html_type='span',
                                          classes={'breadcrumb-separator'}),
                    html.ContainerElement(name, html_type='a', classes={'breadcrumb'}, additional={'href': location})
                ]:
                    yield i

        return html.ContainerElement(*list(acc()), classes={'breadcrumbs'})