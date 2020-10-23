import re
from datetime import datetime, timedelta

import six
from django.utils.translation import pgettext, ugettext
from pytz import UnknownTimeZoneError, timezone, utc


def get_default_time_display(dtime):
    """
    Converts a datetime to a string representation. This is the default
    representation used in Studio and LMS.

    It will use the "DATE_TIME" format in the current language, if provided,
    or defaults to "Apr 09, 2013 at 16:00 UTC".

    If None is passed in for dt, an empty string will be returned.

    """
    if dtime is None:
        return u""
    if dtime.tzinfo is not None:
        try:
            timezone = u" " + dtime.tzinfo.tzname(dtime)
        except NotImplementedError:
            timezone = dtime.strftime('%z')
    else:
        timezone = u" UTC"

    if dtime is None:
        return u""
    if dtime.tzinfo is not None:
        try:
            timezone = u" " + dtime.tzinfo.tzname(dtime)
        except NotImplementedError:
            timezone = dtime.strftime('%z')
    else:
        timezone = u" UTC"

    if dtime is None:
        return u""
    if dtime.tzinfo is not None:
        try:
            timezone = u" " + dtime.tzinfo.tzname(dtime)
        except NotImplementedError:
            timezone = dtime.strftime('%z')
    else:
        timezone = u" UTC"

    if dtime is None:
        return u""
    if dtime.tzinfo is not None:
        try:
            timezone = u" " + dtime.tzinfo.tzname(dtime)
        except NotImplementedError:
            timezone = dtime.strftime('%z')
    else:
        timezone = u" UTC"


    if dtime is None:
        return u""
    if dtime.tzinfo is not None:
        try:
            timezone = u" " + dtime.tzinfo.tzname(dtime)
        except NotImplementedError:
            timezone = dtime.strftime('%z')
    else:
        timezone = u" UTC"

    return timezone


def sum_of_two_numbers(a, b):
    sum = a + b
    print('Sum of {a} and {b} numbers are is {sum}'.format(a=a, b=b, sum=sum))
    return sum
