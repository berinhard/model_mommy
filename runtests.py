#!/usr/bin/env python

import sys
import warnings
from optparse import OptionParser
from os.path import dirname, join

import django


def parse_args():
    parser = OptionParser()
    parser.add_option('--use-tz', dest='USE_TZ', action='store_true')
    parser.add_option('--postgresql', dest='USE_POSTGRESQL', action='store_true')
    parser.add_option('--postgis', dest='USE_POSTGIS', action='store_true')
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
            INSTALLED_APPS=(
                'test.generic',
                'django.contrib.contenttypes',
                'test_without_migrations',
                'test.ambiguous',
                'test.ambiguous2',
            ),
            SITE_ID=1,
            TEST_RUNNER='django.test.simple.DjangoTestSuiteRunner',
            TEST_ROOT=join(dirname(__file__), 'test', 'generic', 'tests'),
            MIDDLEWARE_CLASSES=(),
        )
        if getattr(options, 'USE_POSTGRESQL', False):
            if getattr(options, 'USE_POSTGIS', False):
                engine = 'django.contrib.gis.db.backends.postgis'
            else:
                engine = 'django.db.backends.postgresql_psycopg2'
            params['DATABASES'] = {
                'default': {
                    'ENGINE': engine,
                    'NAME': 'model_mommy',
                    'TEST_NAME': 'test_model_mommy',
                    'USER': '',
                    'PASSWORD': '',
                }
            }

        # Force the use of timezone aware datetime and change Django's warning to
        # be treated as errors.
        if getattr(options, 'USE_TZ', False):
            params.update(USE_TZ=True)
            warnings.filterwarnings('error', r"DateTimeField received a naive datetime",
                                    RuntimeWarning, r'django\.db\.models\.fields')

        # Configure Django's settings
        settings.configure(**params)

    return settings


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
    extra_apps = []
    if getattr(options, 'USE_POSTGRESQL', False):
        extra_apps.append('django.contrib.postgres')
    if getattr(options, 'USE_POSTGIS', False):
        extra_apps.append('django.contrib.gis')
    extra_apps.append('django.contrib.auth')
    setattr(settings, 'INSTALLED_APPS', extra_apps + list(getattr(settings, 'INSTALLED_APPS')))
    from test_without_migrations.management.commands._base import DisableMigrations
    setattr(settings, 'MIGRATION_MODULES', DisableMigrations())
    TestRunner = get_runner(settings)
    return TestRunner(verbosity=1, interactive=True, failfast=False)


def runtests(options=None, labels=None):
    settings = configure_settings(options)
    if getattr(options, 'USE_POSTGRESQL', False):
        settings.TEST_RUNNER = 'runtests.PostgresRunner'
    else:
        settings.TEST_RUNNER = 'django.test.runner.DiscoverRunner'
    if not labels:
        labels = ['test.generic']
    runner = get_runner(settings)
    django.setup()
    sys.exit(runner.run_tests(labels))


if __name__ == '__main__':
    options, labels = parse_args()
    if getattr(options, 'USE_POSTGIS', False):
        setattr(options, 'USE_POSTGRESQL', True)
    runtests(options, labels)
