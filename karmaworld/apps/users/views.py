#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation
from itertools import chain

from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.views.generic.list import MultipleObjectMixin
from karmaworld.apps.notes.models import Note
from karmaworld.apps.users.models import ALL_KARMA_EVENT_CLASSES


class ProfileView(TemplateView, MultipleObjectMixin):
    model = User
    context_object_name = 'user' # name passed to template
    template_name = 'user_profile.html'

    @staticmethod
    def compareProfileItems(a, b):
        if a.__class__ == Note:
            timestampA = a.uploaded_at
        else:
            timestampA = a.timestamp

        if b.__class__ == Note:
            timestampB = b.uploaded_at
        else:
            timestampB = b.timestamp

        if timestampA < timestampB:
            return -1
        elif timestampA > timestampB:
            return 1
        else:
            return 0

    def get_context_data(self, **kwargs):
        notes = [('note', o) for o in Note.objects.filter(user=self.request.user)]
        all_events = []
        for cls in ALL_KARMA_EVENT_CLASSES:
            all_events.append(
                [(cls.__name__, o) for o in cls.objects.filter(user=self.request.user)]
            )
        all_events = chain.from_iterable(all_events)

        result_list = sorted(chain(notes, all_events),
                             cmp=ProfileView.compareProfileItems,
                             key=lambda o: o[1],
                             reverse=True)

        kwargs['object_list'] = result_list

        return super(ProfileView, self).get_context_data(**kwargs)

