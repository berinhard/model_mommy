# -*- coding: utf-8 -*-
from django.test import TestCase

from model_mommy.utils import import_if_str

from test.generic.models import User


class TestUtils(TestCase):

    def test_import_from_str(self):
        self.assertRaises(AttributeError,
                          import_if_str, 'test.generic.UndefinedObject')
        self.assertRaises(ImportError,
                          import_if_str, 'test.generic.undefined_path.User')
        self.assertEqual(User, import_if_str('test.generic.models.User'))

    def test_import_if_str(self):
        self.assertRaises(AttributeError,
                          import_if_str, 'test.generic.UndefinedObject')
        self.assertRaises(ImportError,
                          import_if_str, 'test.generic.undefined_path.User')
        self.assertEqual(User, import_if_str('test.generic.models.User'))
        self.assertEqual(User, import_if_str(User))