#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2014  FinalsClub Foundation
import string
from django import template

register = template.Library()

@register.filter()
def ordinal_letter(value):
    try:
        num = int(value)
        result = num
        if num >= 0 and num < 26:
            result = string.ascii_uppercase[num]
        return result
    except ValueError:
        return value


@register.filter
def keyvalue(dict, key):
    return dict[key]


@register.filter()
def can_edit(user,note):
    return note.allows_edit_by(user)


@register.filter()
def can_tag(user,note):
    return note.allows_tags_by(user)


@register.filter()
def can_del(user,note):
    return note.allows_delete_by(user)
