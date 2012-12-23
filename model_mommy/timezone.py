# coding: utf-8
'''
Add support for Django 1.4+ safe datetimes.
https://docs.djangoproject.com/en/1.4/topics/i18n/timezones/
'''

from datetime import datetime

try:
    from django.utils.timezone import now, utc
except ImportError:
    now = lambda: datetime.now()
