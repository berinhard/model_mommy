# -*- coding: utf-8 -*-
import importlib
import datetime
import itertools

from .timezone import tz_aware
from six import string_types

# Python 2.6.x compatibility code
itertools_count = itertools.count
try:
    itertools_count(0, 1)
except TypeError:
    def count(start=0, step=1):
        n = start
        while True:
            yield n
            n += step
    itertools_count = count


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


def _total_secs(td):
    """
    python 2.6 compatible timedelta total seconds calculation
    backport from
    https://docs.python.org/2.7/library/datetime.html#datetime.timedelta.total_seconds
    """
    if hasattr(td, 'total_seconds'):
        return td.total_seconds()
    else:
        #py26
        return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10.0**6


def seq(value, increment_by=1):
    if type(value) in [datetime.datetime, datetime.date,  datetime.time]:
        if type(value) is datetime.date:
            date = datetime.datetime.combine(value, datetime.datetime.now().time())
        elif type(value) is datetime.time:
            date = datetime.datetime.combine(datetime.date.today(), value)
        else:
            date = value
        # convert to epoch time
        start = _total_secs((date - datetime.datetime(1970, 1, 1)))
        increment_by = _total_secs(increment_by)
        for n in itertools_count(increment_by, increment_by):
            series_date = tz_aware(datetime.datetime.utcfromtimestamp(start + n))
            if type(value) is datetime.time:
                yield series_date.time()
            elif type(value) is datetime.date:
                yield series_date.date()
            else:
                yield series_date
    else:
        for n in itertools_count(increment_by, increment_by):
            yield value + type(value)(n)
