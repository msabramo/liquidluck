#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import shutil
import datetime


def to_unicode(value):
    if isinstance(value, unicode):
        return value
    if isinstance(value, basestring):
        return value.decode('utf-8')
    if isinstance(value, int):
        return str(value)
    return value


def utf8(value):
    if isinstance(value, (bytes, type(None), str)):
        return value
    if isinstance(value, int):
        return str(value)
    assert isinstance(value, unicode)
    return value.encode('utf-8')


def import_object(name):
    if '.' not in name:
        return __import__(name)

    parts = name.split('.')
    obj = __import__('.'.join(parts[:-1]), None, None, [parts[-1]], 0)
    return getattr(obj, parts[-1])


def walk_dir(dest):
    for root, dirs, files in os.walk(dest):
        for f in files:
            path = os.path.join(root, f)
            yield path


def copy_to(source, dest):
    if os.path.exists(dest) and \
       os.stat(source).st_mtime <= os.stat(dest).st_mtime:
        return

    folder = os.path.split(dest)[0]
    # on Mac OSX, `folder` == `FOLDER`
    # then make sure destination is lowercase
    if not os.path.isdir(folder):
        os.makedirs(folder)

    shutil.copy(source, dest)
    return


class UnicodeDict(dict):
    def __getattr__(self, key):
        try:
            return to_unicode(self[key])
        except KeyError:
            return None

    def __setattr__(self, key, value):
        self[key] = to_unicode(value)

    def __getitem__(self, key):
        return to_unicode(super(UnicodeDict, self).__getitem__(key))

    def __setitem__(self, key, value):
        return super(UnicodeDict, self).__setitem__(key, to_unicode(value))


def cjk_nowrap(text):
    start = u'\u4e00'
    end = u'\u9fff'
    pattern = ur'([%s-%s]+?)' % (start, end)
    cjk = re.compile(pattern + r'(\n|\r\n|\r)' + pattern)
    text = cjk.sub(r'\1\3', text)
    return text


def to_datetime(value):
    if isinstance(value, datetime.datetime):
        return value
    supported_formats = [
        '%a %b %d %H:%M:%S %Y',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%dT%H:%M',
        '%Y%m%d %H:%M:%S',
        '%Y%m%d %H:%M',
        '%Y-%m-%d',
        '%Y%m%d',
    ]
    for format in supported_formats:
        try:
            return datetime.datetime.strptime(value, format)
        except ValueError:
            pass
    raise ValueError('Unrecognized date/time: %r' % value)
