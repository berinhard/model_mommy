#!/usr/bin/env python

from os.path import dirname, join
import sys
from optparse import OptionParser


def parse_args():
    parser = OptionParser()
    options, args = parser.parse_args()

    # Build labels
    if args:
        labels = ["model_mommy.%s" % label for label in args]
    else:
        labels = ['model_mommy']

    return options, labels


def configure_settings():
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
                'model_mommy',
            ),
            SITE_ID=1,
            TEST_ROOT=join(dirname(__file__), 'model_mommy', 'tests'),
        )

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
    settings = configure_settings()
    runner = get_runner(settings)
    sys.exit(runner.run_tests(test_labels))


if __name__ == '__main__':
    runtests()
