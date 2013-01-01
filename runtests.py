#!/usr/bin/env python

from os.path import dirname, join
import sys
from optparse import OptionParser
import warnings


def parse_args():
    parser = OptionParser()
    parser.add_option('--use-tz', dest='USE_TZ', action='store_true')
    options, args = parser.parse_args()

    # Build labels
    if args:
        labels = ["generic.%s" % label for label in args]
    else:
        labels = ['generic']

    return options, labels


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
            ),
            SITE_ID=1,
            TEST_ROOT=join(dirname(__file__), 'test', 'generic', 'tests'),
        )

        # Force the use of timezone aware datetime and change Django's warning to
        # be treated as errors.
        if options.USE_TZ:
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
    return TestRunner(verbosity=1, interactive=True, failfast=False)


def runtests():
    options, test_labels = parse_args()
    settings = configure_settings(options)
    runner = get_runner(settings)
    sys.exit(runner.run_tests(test_labels))


if __name__ == '__main__':
    runtests()
