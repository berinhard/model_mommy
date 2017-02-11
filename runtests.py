#!/usr/bin/env python

from os.path import dirname, join
import sys
from optparse import OptionParser
import warnings
import django

def parse_args():
    parser = OptionParser()
    parser.add_option('--use-tz', dest='USE_TZ', action='store_true')
    parser.add_option('--postgresql', dest='USE_POSTGRESQL', action='store_true')
    return parser.parse_args()

def configure_settings(options):
    from django.conf import settings

    # If DJANGO_SETTINGS_MODULE envvar exists the settings will be
    # configured by it. Otherwise it will use the parameters bellow.
    if not settings.configured:
        params = dict(
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS = (
                'test.generic',
                'django.contrib.contenttypes',
                'test_without_migrations',
                'test.ambiguous',
                'test.ambiguous2',
            ),
            SITE_ID=1,
            TEST_RUNNER='django.test.simple.DjangoTestSuiteRunner',
            TEST_ROOT=join(dirname(__file__), 'test', 'generic', 'tests'),
        )
        if getattr(options, 'USE_POSTGRESQL', False):
            params['DATABASES'] = {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql_psycopg2',
                    'NAME': 'model_mommy',
                    'TEST_NAME': 'test_model_mommy',
                    'USER': 'postgres',
                }
            }

        if django.VERSION >= (1, 7):
            params.update(
                MIDDLEWARE_CLASSES=tuple()
            )

        # Force the use of timezone aware datetime and change Django's warning to
        # be treated as errors.
        if getattr(options, 'USE_TZ', False):
            params.update(USE_TZ=True)
            warnings.filterwarnings('error', r"DateTimeField received a naive datetime",
                                    RuntimeWarning, r'django\.db\.models\.fields')

        # Configure Django's settings
        settings.configure(**params)

    return settings

if django.VERSION >= (1, 8):
    # We only need this if HstoreFields are a possibility
    from django.db.backends.signals import connection_created
    from django.test.runner import DiscoverRunner

    def create_hstore(sender, **kwargs):
        conn = kwargs.get('connection')
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute('CREATE EXTENSION IF NOT EXISTS HSTORE')

    class PostgresRunner(DiscoverRunner):
        """Create HStore extension before test database is created"""

        def setup_databases(self):
            connection_created.connect(create_hstore)
            result = super(PostgresRunner, self).setup_databases()
            connection_created.disconnect(create_hstore)
            return result


def get_runner(settings):
    '''
    Asks Django for the TestRunner defined in settings or the default one.
    '''
    from django.test.utils import get_runner
    if getattr(options, 'USE_POSTGRESQL', False) and django.VERSION >= (1, 8):
        setattr(settings, 'INSTALLED_APPS',
                ['django.contrib.postgres']
                + list(getattr(settings, 'INSTALLED_APPS')))
    if django.VERSION >= (1, 7):
        #  I suspect this will not be necessary in next release after 1.7.0a1:
        #  See https://code.djangoproject.com/ticket/21831
        setattr(settings, 'INSTALLED_APPS',
                ['django.contrib.auth']
                + list(getattr(settings, 'INSTALLED_APPS')))
        from test_without_migrations.management.commands.test import DisableMigrations
        setattr(settings, 'MIGRATION_MODULES', DisableMigrations())
    TestRunner = get_runner(settings)
    return TestRunner(verbosity=1, interactive=True, failfast=False)


def runtests(options=None, labels=None):
    settings = configure_settings(options)
    if django.VERSION >= (1, 8):
        if getattr(options, 'USE_POSTGRESQL', False):
            settings.TEST_RUNNER = 'runtests.PostgresRunner'
        else:
            settings.TEST_RUNNER = 'django.test.runner.DiscoverRunner'
        if not labels:
            labels = ['test.generic']
    else:
        if not labels:
            labels = ['generic']
    runner = get_runner(settings)
    if django.VERSION >= (1, 7):
        django.setup()
    sys.exit(runner.run_tests(labels))


if __name__ == '__main__':
    options, labels = parse_args()
    runtests(options, labels)
