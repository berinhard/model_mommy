#!/usr/bin/env python

from os.path import dirname, join
import sys
from optparse import OptionParser
import warnings
import django


def parse_args():
    parser = OptionParser()
    parser.add_option('--use-tz', dest='USE_TZ', action='store_true')
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
                'django.contrib.contenttypes',
                'test.generic',
                'test.ambiguous',
                'test.ambiguous2',
            ),
            SITE_ID=1,
            TEST_RUNNER='django.test.simple.DjangoTestSuiteRunner',
            TEST_ROOT=join(dirname(__file__), 'test', 'generic', 'tests'),
        )

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


def get_runner(settings):
    '''
    Asks Django for the TestRunner defined in settings or the default one.
    '''
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)
    if django.VERSION >= (1, 7):
        #  I suspect this will not be necessary in next release after 1.7.0a1:
        #  See https://code.djangoproject.com/ticket/21831
        setattr(settings, 'INSTALLED_APPS',
                ['django.contrib.auth']
                + list(getattr(settings, 'INSTALLED_APPS')))
    return TestRunner(verbosity=1, interactive=True, failfast=False)


def runtests(options=None, labels=None):
    settings = configure_settings(options)
    if django.VERSION >= (1, 8):
        settings.TEST_RUNNER='django.test.runner.DiscoverRunner'
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
