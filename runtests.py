#!/usr/bin/env python

import os
import sys

parent = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, parent)

os.environ['DJANGO_SETTINGS_MODULE'] = 'test_settings'


def runtests():
    args = sys.argv[1:]
    if args:
        test_labels = ["model_mommy.%s" % arg for arg in args]
    else:
        test_labels = ['model_mommy']

    try:
        from django.test.simple import run_tests
        result = run_tests(test_labels, 1, True)
        sys.exit(result)
    except ImportError:
        from django.test.simple import DjangoTestSuiteRunner
        test_suite = DjangoTestSuiteRunner(1, True)
        result = test_suite.run_tests(test_labels)
        sys.exit(result)


if __name__ == '__main__':
    runtests()
