from collections import ChainMap
from functools import wraps

from . import Config, DefaultConfig
from .controller import Controller, controller_mapper
from .model import Model
from dynct.util.misc_decorators import apply_to_type
from dynct.util.typesafe import typesafe

__author__ = 'justusadam'


class Autoconf:
    """
    Chains Custom config, model config and default conf and assigns it to the model.

    Priority is given as follows:
     Model.config > custom config argument? > Controller.config? > DefaultConfig
     ? is optional, will be omitted if bool(?) == false
    """
    @typesafe
    def __init__(self, conf:Config=None):
        self.custom_conf = conf

    def __call__(self, func):
        @wraps(func)
        @apply_to_type(Model, Controller)
        def wrap(model, controller):
            model.config = ChainMap(*[a for a in [
                model.config,
                self.custom_conf,
                self.get_controller_conf(controller),
                DefaultConfig
                ]
            if a])
        return wrap

    def get_controller_conf(self, controller):
        return controller.config if hasattr(controller, 'config') else None


def controller(prefix):
    def wrap(func):
        controller_mapper[prefix].append(func)
        return func