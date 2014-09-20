from .commons import MenuHandler, CommonsHandler
from . import database_operations as dbo

__author__ = 'justusadam'


name = 'commons_engine'

role = 'block_manager'


def common_handler(item_type, item_name):
    handlers = {
        'menu': MenuHandler,
        'common': CommonsHandler
    }
    return handlers[item_type](item_name)

def prepare():
    mo = dbo.MenuOperations()
    mo.init_tables()
    mo.add_menu('start_menu', 'Start Menu', True)
    mo.add_menu_item('welcome', 'Welcome', '/iris/1', 'start_menu', True, '<root>', 1)
    mo.add_menu_item('testpage', 'Hello World', '/iris/2', 'start_menu', True, '<root>', 2)
    mo.add_menu_item('setup', 'Restart Setup', '/setup', 'start_menu', True, 'welcome', 1)