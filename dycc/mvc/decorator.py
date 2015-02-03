__doc__ = """
This module defines decorators to use for registering and interacting
with the dynamic_content model-view-controller implementation

Important interactions are:

 Registering a new view/controller function:

  Annotate the function with @controller_function(*args) or
   @rest_controller_function(*args)

  ... more doc to follow

  **options allow you to specify further flags and options that
  might be interesting to other parts of the framework,
  mostly used by view middleware

  known options are:

   anti_csrf (boolean, default=True):  when set to false no anti-csrf token
    checking is performed on requests to the path handled by this controller
   require_ssl (boolean, default=False): when set to true a middleware will
    redirect any http request to this controller to the appropriate https url
    provided the server currently has https enabled


It is recommended to not directly use ControllerFunction and
RestControllerFunction.
"""

import functools

from .. import _component
from dycc import http
from .context import apply_to_context
from dycc.util import rest


__author__ = 'Justus Adam'
__version__ = '0.2'


controller_mapper = _component.get_component('PathMap')


def _to_set(my_input, allowed_vals=str):
    if isinstance(my_input, (list, tuple, set, frozenset)):
        for i in my_input:
            if not isinstance(i, allowed_vals):
                raise TypeError(
                    'Expected type {} got {}'.format(
                        allowed_vals, type(my_input))
                        )
        return frozenset(my_input)
    elif isinstance(my_input, allowed_vals):
        return frozenset({my_input})
    else:
        raise TypeError('Expected type {} or {} got {}'.format(
            (list, tuple, set, frozenset), allowed_vals, type(my_input)
            ))


class ControlFunction(object):
    def __init__(self, function, value, method, query, headers, options=None):
        if isinstance(function, ControlFunction):
            self.function = function.function
            self.wrapping = function.wrapping
        else:
            self.wrapping = []
            self.function = function
        self.wrapping.append(self)
        self.value = _to_set(value)
        self.method = _to_set(method, str)
        self.query = query if isinstance(query, (dict, bool)) else _to_set(query)
        self.headers = None if headers is None else _to_set(headers)
        self.instance = None
        self.typeargs = []
        self.options = options if options is not None else {}

    def __call__(self, *args, **kwargs):
        if self.instance:
            return self.function(self.instance, *args, **kwargs)
        return self.function(*args, **kwargs)

    def __repr__(self):
        return '<ControlFunction for path(s) \'{}\' with {}>'.format(
            self.value, self.function
            )


class RestControlFunction(ControlFunction):
    def __call__(self, model, *args, **kwargs):
        model.json_return = super().__call__(*args, **kwargs)
        model.decorator_attributes |= {'no-view', 'json-format', 'string-return'}
        return model


def _controller_function(
    class_,
    value,
    *,
    method=http.RequestMethods.GET,
    headers=None,
    query=False,
    **options
    ):
    def wrap(func):
        wrapped = class_(func, value, method, query, headers, options)
        for val in wrapped.value:
            controller_mapper.add_path(val, wrapped)
        return wrapped
    return wrap



def _controller_method(
    class_,
    value,
    *,
    method=http.RequestMethods.GET,
    headers=None,
    query=False,
    **options
    ):
    def wrap(func):
        wrapped = class_(func, value, method, query, headers, options)
        return wrapped
    return wrap


controller_function = functools.partial(_controller_function, ControlFunction)


def controller_class(class_):
    c_funcs = tuple(filter(
        lambda a: isinstance(a, ControlFunction),
        class_.__dict__.values()
        ))
    if c_funcs:
        instance = class_()
        controller_mapper._controller_classes.append(instance)
        for item in c_funcs:
            for wrapped in item.wrapping:
                wrapped.instance = instance
                for i in wrapped.value:
                    controller_mapper.add_path(i, wrapped)
    return class_


controller_method = functools.partial(_controller_method, ControlFunction)

rest_controller_function = functools.partial(_controller_function, RestControlFunction)

rest_controller_method = functools.partial(_controller_method, RestControlFunction)


@apply_to_context(return_from_decorator=True, with_return=True)
def json_return(context, res):
    return rest.json_response(res, context)