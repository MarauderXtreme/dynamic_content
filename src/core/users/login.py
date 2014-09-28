import datetime

from framework.html_elements import FormElement, TableElement, ContainerElement, Label, Input, SubmitButton
from core import handlers
from core.users.client import ANONYMOUS
from . import session


__author__ = 'justusadam'

login_prefix = 'login'
logout_prefix = 'logout'

_cookie_time_format = '%a, %d %b %Y %H:%M:%S GMT'

USERNAME_INPUT = Label('Username', label_for='username'), Input(name='username', required=True)
PASSWORD_INPUT = Label('Password', label_for='password'), Input(input_type='password', required=True, name='password')

LOGOUT_TARGET = '/login'

LOGOUT_BUTTON = ContainerElement('Logout', html_type='a', classes={'logout', 'button'},
                                 additionals={'href': '/' + logout_prefix})

LOGIN_FORM = FormElement(
  TableElement(
    USERNAME_INPUT,
    PASSWORD_INPUT
  )
  , action='/' + login_prefix, classes={'login-form'}, submit=SubmitButton(value='Login')
)

LOGIN_COMMON = FormElement(
  ContainerElement(
    *USERNAME_INPUT + PASSWORD_INPUT
  )
  , action='/' + login_prefix, classes={'login-form'}, submit=SubmitButton(value='Login')
)


class LoginHandler(handlers.PageContent, handlers.RedirectMixIn):
  def __init__(self, url, parent_handler):
    super().__init__(url, parent_handler)
    self.message = ''
    self.page_title = 'Login'

  def process_content(self):
    ContainerElement('Your Login failed, please try again.', classes={'alert'})
    return ContainerElement(self.message, LOGIN_FORM)

  def process_post(self):
    if not self.url.post['username'] or not self._url.post['password']:
      raise ValueError
    username = self.url.post['username'][0]
    password = self.url.post['password'][0]
    token = session.start_session(username, password)
    if token:
      self.add_morsels({'SESS': token})
      self.redirect('/iris/1')


class LoginCommonHandler(handlers.Commons):
  source_table = 'user_management'

  def get_content(self, name):
    return LOGIN_COMMON


class LogoutHandler(handlers.PageContent, handlers.RedirectMixIn):
  def process_content(self):
    self.logout()

  def logout(self):
    user = self._parent.client.user
    if user == ANONYMOUS:
      self.redirect('/login')
    else:
      session.close_session(user)
      time = datetime.datetime.utcnow() - datetime.timedelta(days=1)
      self.add_morsels({'SESS': ''})
      self.cookies['SESS']['expires'] = time.strftime(_cookie_time_format)
      self.redirect('/login')