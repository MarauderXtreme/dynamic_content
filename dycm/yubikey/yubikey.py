import dycc
from dycc import hooks, route
from dycc.includes import log
from dycm.users import login, model, users
from dycc.util import html, console
from dycc.backend import orm
import yubico_client
from yubico_client import yubico_exceptions

__author__ = 'MarauderXtreme'
__version__ = '0.1'


input_name = 'yubikey'

# @route.controller_function(
#
# )
# def yubikey_admin_page


@dycc.inject('settings')
def get_client(settings):
    yid, key = settings['yubikey_id'], settings['yubikey_key']
    return yubico_client.Yubico(yid, key)


@hooks.register()
class Yubikey(login.LoginHook):

    def handle_form(self, form: html.FormElement):
        yubi_input = html.Div(
            html.Label(
                'Yubikey:',
                label_for='yubikey'
            ),
            html.Input(
                classes={input_name, 'yubikey-login', 'login'},
                name=input_name,
                element_id=input_name,
                input_type='text'
            ),
            'Optional until assigned'
        )
        form.content.append(
            yubi_input
        )

    def handle_login_request(self, query):

        user = users.get_single_user(query['username'][0])

        keys = list(YubikeyDB.select(YubikeyDB.yubikey).where(user=user))

        if len(keys) == 0:
            return True

        if not input_name in query:
            return False

        key = query[input_name][0]

        try:
            return get_client().verify(key)
        # except yubico_exceptions.SignatureVerificationError as validation_fail:
        #     return False
        except yubico_exceptions.YubicoError as yubikey_error:
            log.write_error(yubikey_error)
            console.print_error(yubikey_error)
            return False


class YubikeyDB(orm.BaseModel):

    yubikey = orm.CharField(max_length=12)
    user = orm.ForeignKeyField(model.User)

