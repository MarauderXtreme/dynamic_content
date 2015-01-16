from ._component import (component, get_component, call_component,
                        Component, inject, inject_method)
from . import model, _registry, mvc
from dyc.modules.cms.model import ContentTypes, ContentHandler
from dyc.modules.theming import Theme


__author__ = 'Justus Adam'
__version__ = '0.1'


Modules = get_component('modules')


def add_content_handler(handler_name, handler, prefix):
    return ContentHandler(module=handler, machine_name=handler_name, path_prefix=prefix).save()


def add_theme(name, enabled=False):
    return Theme.create(machine_name=name, enabled=enabled)


def get_module(name):
    return model.Module.get(machine_name=name)


def get_theme(name):
    return Theme.get(machine_name=name)


def get_content_type(name):
    return ContentTypes.get(machine_name=name)


get_ct = get_content_type
