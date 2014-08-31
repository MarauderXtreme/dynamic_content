from coremodules.olymp.basic_page_handlers import SimplePageHandler

__author__ = 'justusadam'


class IrisPageHandler(SimplePageHandler):

    def __init__(self, page_id, get_query):
        super().__init__(page_id=page_id, get_query=get_query)
        self.content_type = self.get_content_type()
        self.page_type = 'iris'

    def get_content(self):
        pass

    def get_title(self):
        pass


class EditIrisHandler(IrisPageHandler):
    pass