from http.server import BaseHTTPRequestHandler
from io import BytesIO
import sys
import shutil

from .database import DatabaseError, Database, escape
from .basic_page_handlers import FileHandler, BasicPageHandler
from tools.http_tools import split_path, join_path, parse_url
from tools.config_tools import read_config
from pathlib import Path


__author__ = 'justusadam'


class RequestHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)
        self.page_handler = None
        self.db = None

    def do_POST(self):
        if not self.check_path():
            return 0

        get_handler_response = self.get_handler()
        if get_handler_response != 0:
            self.send_error(get_handler_response, *self.responses[get_handler_response])
            return 0

        post_request = self.rfile.read(int(self.headers['Content-Length'])).decode()

        if self.page_handler.process_post(post_request):
            self.send_response(302, *self.responses[302])
            self.send_header("Location", self.get_post_target())
            self.end_headers()
        else:
            self.send_document()

        return 0

    def do_GET(self):
        if not self.check_path():
            return 0

        get_handler_response = self.get_handler()
        if get_handler_response != 0:
            self.send_error(get_handler_response, *self.responses[get_handler_response])
            return 0

        self.send_document()

        return 0

    def send_document(self):
        enc = sys.getfilesystemencoding()
        handler_response = self.page_handler.compile_page()
        if not handler_response:
            # TODO send some generic error if handler rejects request
            return
        if handler_response == 200 or handler_response is True:
            encoded = self.page_handler.document.encode(enc)
            self.send_response(200)
            self.send_header("Content-type", "{content_type}; charset={encoding}".format(
                content_type=self.page_handler.content_type, encoding=enc))
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            stream = BytesIO()
            stream.write(encoded)
            stream.seek(0)
            try:
                shutil.copyfileobj(stream, self.wfile)
            finally:
                stream.close()
        else:
            self.send_error(handler_response, *self.responses[handler_response])
            return

    def get_post_target(self):
        (path, location, query) = split_path(self.path)
        if query:
            for option in query.split('?'):
                option = option.split('=')
                if option[0] == 'destination':
                    return '/' + option[1]
        return '/'

    def check_path(self):

        (path, location, query) = split_path(path=self.path)

        if path.endswith('/') and path != '/':
            self.send_response(301)
            self.send_header("Location", join_path(path[:-1], location, query))
            self.end_headers()
            return False
        return True

    def get_handler(self):
        bootstrap = read_config('includes/bootstrap')

        (path, location,  get_query) = parse_url(url=self.path)
        if len(path) > 0:
            if path[0] == 'setup':
                if not read_config(str(Path(__file__).parent / 'config.json'))['setup']:
                    return 404
                if len(path) == 1:
                    page_id = 0
                else:
                    page_id = int(path[1])
                from .setup import page_handler_factory
                self.page_handler = page_handler_factory(page_id=page_id, get_query=get_query)
                return 0
            elif path[0] in bootstrap['FILE_DIRECTORIES'].keys():
                self.page_handler = FileHandler(path)
                return 0
        try:
            self.db = Database()
        except DatabaseError:
            # TODO figure out which error to raise if database unreachable, currently 'internal server error'
            return 500

        path = self.de_alias(path)

        if len(path) == 0:
            return 404

        return BasicPageHandler(path, get_query)

    def get_content_handler_module(self, path_prefix):
        handler_id = self.db.select('handler_module', 'content_handlers', 'where path_prefix = ' + escape(path_prefix).fetchone())
        if handler_id is None:
            return None
        handler_id = handler_id[0]
        handler_path = self.db.select('module_path', 'modules', 'where id = ' + escape(handler_id))

        if handler_path is None:
            return None
        return handler_path[0].replace('/', '.')

    def de_alias(self, path):
        if len(path) == 0:
            alias = '/'
        else:
            alias = '/' + '/'.join([word for word in path])
        try:
            source = self.translate_alias(alias)
            return source.split('/')
        except DatabaseError:
            return path

    def translate_alias(self, alias):
        query_result = self.db.select('source', 'alias', 'where alias = ' + escape(alias)).fetchone()
        if query_result is None:
            query_result = alias
        else:
            query_result = query_result[0]
        return query_result