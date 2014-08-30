from http.server import *

from tools.http_tools import split_path, join_path
from coremodules.olymp.request_handler import RequestHandler
from tools.config_tools import read_config


__author__ = 'justusadam'


def main():

    #test()

    run(handler_class=RequestHandler)

    return 0


def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    config = read_config('config')
    server_address = (config['server_arguments']['host'], config['server_arguments']['port'])
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


def test():
    one = {'one': 'hello', 'much_fun': 'more'}
    two = {'bla': 'blabla', 'things': 'stuff'}

    one.update(**two)

    print(one)

    testpath = '/neu/bla/'
    testpath2 = '/jaja/haba'

    print(join_path(*split_path(testpath)))
    print(join_path(*split_path(testpath2)))


if __name__ == '__main__':
    main()
