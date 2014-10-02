from ..database_operations import Operations, escape

__author__ = 'justusadam'


class AdminOperations(Operations):
  _queries = {
    'mysql': {
      'get_all_categories': 'select machine_name, display_name from admin_categories {cond} order by weight;',
      'get_subcategories': 'select machine_name, display_name, category from admin_subcategories {cond} order by category, weight;',
      'get_page': 'select handler_module from admin_pages where machine_name={machine_name};',
      'get_cat_pages': 'select machine_name, display_name, handler_module from admin_pages where subcategory={category};'
    }
  }

  _tables = {'admin_categories', 'admin_subcategories', 'admin_pages'}

  def get_categories(self, *categories):
    cond = ''
    if categories:
      acc = []
      for item in categories:
        acc.append('machine_name=' + escape(item))
      cond = 'where ' + ' and '.join(acc)
    self.execute('get_all_categories', cond=cond)
    return self.cursor.fetchall()

  def get_subcategories(self, *categories):
    cond = ''
    if categories:
      acc = []
      for item in categories:
        acc.append('category=' + escape(item))
      cond = 'where ' + ' and '.join(acc)
    self.execute('get_subcategories', cond=cond)
    return self.cursor.fetchall()

  def get_page(self, name):
    self.execute('get_page', machine_name=escape(name))
    return self.cursor.fetchone()[0]

  def get_cat_pages(self, category):
    self.execute('get_cat_pages', category=escape(category))
    return self.cursor.fetchall()