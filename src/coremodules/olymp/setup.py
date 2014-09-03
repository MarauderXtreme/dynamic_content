from .database import DatabaseError, Database
from .basic_page_handlers import PageHandler
from .module_operations import Module
from ..aphrodite import ContainerElement, Stylesheet, List, TableElement, FormElement, Input
from tools.config_tools import read_config


__author__ = 'justusadam'


def try_database_connection():
    try:
        test_database = Database()
        if test_database.check_connection():
            return ContainerElement(
                'The connection with the database was successfully established, you may continue with this setup',
                html_type='p') + ContainerElement('Continue', html_type='a', classes=['continue', 'button'],
                                                  additionals=['href="/setup/{next_page}"'])
        else:
            return ContainerElement(
                'The connection with the database could not be established. Please review your settings '
                'and then reload this page', html_type='p')
    except DatabaseError:
        return ContainerElement(
            'The connection with the database could not be established. Please review your settings and then '
            'reload this page', html_type='p')


class SetupHandler(PageHandler):
    def __init__(self, url):
        super().__init__(url)
        self.bootstrap = read_config('includes/bootstrap')

    def compile_page(self):
        config = read_config('config')
        setup_pages = {
            0: {
                'title': 'Setup of your CMS Installation',
                'content': str(
                    ContainerElement(
                        ContainerElement('Welcome to the setup process of your python_cms content management system.',
                        html_type='p'),
                        ContainerElement('These pages will guide you trough the necessary steps and tests that need to be taken to ensure python_cms will function properly for you.', html_type='p'),
                        ContainerElement('During this process you will be required to enter and confirm sensible data to your installation as well as set a password for the administration user. It is therefore recommended that you perform this setup directly on the server or ahead of deployment or utilizing a secure and encrypted connection.', html_type='p'),
                        ContainerElement(
                        'I hope that you will enjoy and be pleased with python_cms.', html_type='p'),
                        ContainerElement('Continue', html_type='a', classes=['continue', 'button'],
                                                                 additionals=['href="/setup/{next_page}"'])
                    )
                )
            },
            1: {
                'title': 'Overview',
                'content': str(
                    ContainerElement(
                        ContainerElement('The following steps will be taken during this setup', html_type='h3'),
                        List(
                            'Verifying Database Information',
                            'Configure site information',
                            'Set up an admin user',
                            list_type='ul'
                        ),
                        ContainerElement('Continue', html_type='a', classes=['continue', 'button'],
                                        additionals=['href="/setup/{next_page}"'])
                    )
                )
            },
            2: {
                'title': 'Verifying Database Configuration',
                'content':
                str(
                    ContainerElement(
                        TableElement(
                            ['Type', config['database_type']],
                            ['Host', config['database_connection_arguments']['host']],
                            ['Database Name', config['database_connection_arguments']['database']],
                            ['User', config['database_connection_arguments']['user']],
                            ['Password', config['database_connection_arguments']['passwd']]),
                            ContainerElement('Please verify that these settings are correct or change '
                                             'them accordingly in the \'config.json\' file.',
                                             html_type='p'),
                            try_database_connection()
                    )
                )
            },
            3: {
                'title': 'Executing initial queries on the database',
                'content': str(
                    ContainerElement(
                        ContainerElement(
                            'The following step will execute the initial queries to the database requred for python_cms to function. This will create new tables and fill them according to the installation specifications provided sufficient access to the database has been granted.',html_type='p'),
                        ContainerElement('This step is required to proceed', html_type='p'),
                        ContainerElement(
                            'If you are certain, that the database has been properly configured to allow sufficient access to python_cms and are content with this software making changes to your database please click \'Continue\'', html_type='p'),
                        ContainerElement('Continue', html_type='a', classes=['button', 'continue'],
                                                     additionals='href="/setup/{next_page}"')
                    )
                )
            },
            4: {
                'title': '{result}',
                'content': str(
                    ContainerElement(
                        '{message}',
                         ContainerElement('{link}', html_type='a', classes=['continue', 'button'],
                                                 additionals=['href="{target}"'])))
            },
            5: {
                'title': 'Create an admin account',
                'content': str(
                    ContainerElement(
                        ContainerElement(
                            'This page is a placeholder since the authorization is not yet implemented. Please click submit.', classes='alert'),
                        FormElement(
                            TableElement(
                                ('Name', Input(name='name')),
                                ('Firstname', Input(name='firstname')),
                                ('Username', Input(name='username')),
                                ('Password', Input(name='password')),
                                ('Confirm Password', Input(name='confirm-password'))

                            ), action='{this}?destination=/', element_id='admin_form')
                    )
                )
            }
        }
        generic = {
            'stylesheets': str(Stylesheet('/theme/default_theme/css/style.css')),
            'scripts': '',
            'header': '',
            'footer': str(ContainerElement('Python CMS 2014', element_id='')),
            'pagetitle': 'Setting up your CMS installation'
        }
        replacement_pattern = setup_pages[self._url.page_id]

        replacement_pattern.update(generic)

        setup_template = open('themes/default_theme/template/page.html')
        setup_template = setup_template.read()
        page = setup_template.format(**replacement_pattern)

        if self._url.page_id == 4:
            page = page.format(**self.setup_wrapper())
            page = page.format(this=self._url.path, next_page=self._url.page_id + 1)
        else:
            page = page.format(this=self._url.path, next_page=self._url.page_id + 1)
        self._document = page
        self._has_document = True
        return 200

    def process_post(self, post_query):
        return self._url.page_id == 3

    def setup(self):

        db = Database()

        if 'reset' in self._url.query:
            if self._url.query['reset'].lower() == 'true':
                try:
                    moduleconf = Module().discover_modules()
                    for module in moduleconf:
                        if module['name'] in self.bootstrap['DEFAULT_MODULES'] + [self.bootstrap['CORE_MODULE']]:
                            if 'required_tables' in module:
                                print('dropping tables for ' + module['name'])
                                try:
                                    db.drop_tables(tuple(a['table_name'] for a in module['required_tables']))
                                except DatabaseError as newerror:
                                    print('Could not drop table for ' + module['name'] + ' due to error: ' + str(
                                        newerror.args))
                except DatabaseError as error:
                    print('Database Error in setup: ' + str(error.args))
        try:
            temp = Module()
            temp.is_setup = True
            temp.activate_module('olymp')
            temp.register_installed_modules()
            temp.is_setup = False
            temp._set_module_active('olymp')
            for module in self.bootstrap['DEFAULT_MODULES']:
                if not temp.activate_module(module):
                    print('Could not activate module ' + module)
                    return False
            return True
        except DatabaseError as err:
            print(err)
            return False

    def setup_wrapper(self):
        if self.setup():
            return {
                'result': 'Success',
                'message': str(
                    ContainerElement(
                        ContainerElement('Your installation has been successful.', html_type='p'),
                        ContainerElement('All necessary tables have been created and filled in the database',
                            html_type='p'),
                        ContainerElement('You may proceed.', html_type='p'))),
                'target': '/setup/{next_page}',
                'link': 'Continue'
            }
        else:
            return {
                'result': 'Failed',
                'message': str(
                    ContainerElement(
                        ContainerElement('Your installation has failed.', html_type='p'),
                        ContainerElement('Please revisit you settings and try again.',
                                         html_type='p'),
                        ContainerElement(
                            'Please ensure the database does not contain any tables that this CMS'
                            ' is trying to create', html_type='p'),
                        ContainerElement(
                            'You may delete all existing tables that should be created by clicking reset',
                            html_type='p'),
                ContainerElement('Reset', html_type='a', classes='button',
                                 additionals=['href="/setup/{page_id}?reset=True"']))),
                'target': '/setup',
                'link': 'Restart'
            }
