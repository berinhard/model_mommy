#!/usr/bin/env python

import os
import sys

parent = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, parent)

os.environ['DJANGO_SETTINGS_MODULE'] = 'test_settings'


def runtests():
    try:
        from django.test.simple import run_tests
        result = run_tests(['model_mommy'], 1, True)
        sys.exit(result)
    except ImportError:
        from django.test.simple import DjangoTestSuiteRunner
        test_suite =  DjangoTestSuiteRunner(1, True)
        result = test_suite.run_tests(['model_mommy'])
        sys.exit(result)


if __name__ == '__main__':
    runtests()
