# -*- coding: utf-8 -*-
import django
if django.VERSION >= (1, 7):
    import importlib
else:
    from django.utils import importlib

from six import string_types


def import_if_str(import_string_or_obj):
    """
    Import and return an object defined as import string in the form of

        path.to.module.object_name

    or just return the object if it isn't a string.
    """
    if isinstance(import_string_or_obj, string_types):
        return import_from_str(import_string_or_obj)
    return import_string_or_obj


def import_from_str(import_string):
    """
    Import and return an object defined as import string in the form of

        path.to.module.object_name
    """
    path, field_name = import_string.rsplit('.', 1)
    module = importlib.import_module(path)
    return getattr(module, field_name)

