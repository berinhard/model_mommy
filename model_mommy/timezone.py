# coding: utf-8
'''
Add support for Django 1.4+ safe datetimes.
https://docs.djangoproject.com/en/1.4/topics/i18n/timezones/
'''

from datetime import datetime
from django import VERSION
from django.conf import settings

try:
    from django.utils.timezone import now, utc
except ImportError:
    now = lambda: datetime.now()


def smart_datetime(*args):
    value = datetime(*args)
    return tz_aware(value)

def tz_aware(d):
    value = d
    if VERSION >= (1, 4) and settings.USE_TZ:
        value = d.replace(tzinfo=utc)

    return value
