#!/usr/bin/env python

import os
import sys

parent = os.path.abspath(os.path.dirname(__file__))
tests_dir = os.path.join(parent, 'model_mommy', 'tests')
sys.path.insert(0, parent)
sys.path.insert(0, tests_dir)

os.environ['DJANGO_SETTINGS_MODULE'] = 'test_settings'


def get_runner():
    '''
    Asks Django for the TestRunner defined in settings or the default one.
    '''
    from django.conf import settings
    from django.test.utils import get_runner
    TestRunner = get_runner(settings)
    return TestRunner(verbosity=1, interactive=True, failfast=False)


def runtests():
    args = sys.argv[1:]
    if args:
        test_labels = ["model_mommy.%s" % arg for arg in args]
    else:
        test_labels = ['model_mommy']

    runner = get_runner()
    sys.exit(runner.run_tests(test_labels))


if __name__ == '__main__':
    runtests()
