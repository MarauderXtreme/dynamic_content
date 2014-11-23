from dynct.core.mvc.model import Model
from dynct.util.config import read_config
from dynct.util.misc_decorators import apply_by_type

__author__ = 'justusadam'


@apply_by_type(Model, apply_in_decorator=True)
class NodeProcess:
    def __init__(self, func):
        self.function = func

    def __call__(self, model):
        res = self.function()
        if hasattr(res, '__iter__'):
            content = self._process_nodes(res)
        else:
            content = self._process_single_node(res)
        model['content'] = content
        return 'page'

    def _process_single_node(self, node):
        return open(self._template('single_node_template')).read().format(**node)

    def _process_nodes(self, nodes):
        template = open(self._template('multi_node_template')).read()
        return ''.join([template.format(**a) for a in nodes])

    def _template(self, _type):
        return read_config(__file__ + '/../config')[_type]