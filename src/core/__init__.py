__author__ = 'justusadam'

from .module_operations import register_installed_modules, load_active_modules

name = 'olymp'

role = 'core'

# TODO refactor everything to get core module and move it here


def load_modules(db):
    return load_active_modules(db)