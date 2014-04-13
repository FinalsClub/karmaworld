#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation
from itertools import chain

from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.views.generic.list import MultipleObjectMixin
from karmaworld.apps.users.models import ALL_KARMA_EVENT_CLASSES


class ProfileView(TemplateView, MultipleObjectMixin):
    model = User
    context_object_name = 'user' # name passed to template
    template_name = 'user_profile.html'

    def get_context_data(self, **kwargs):
        all_events = []
        for cls in ALL_KARMA_EVENT_CLASSES:
            all_events.append(
                [(cls.__name__, o) for o in cls.objects.filter(user=self.request.user)]
            )

        result_list = sorted(chain.from_iterable(all_events),
                             key=lambda o: o[1].timestamp,
                             reverse=True)

        kwargs['object_list'] = result_list

        kwargs['badge'] = self.request.user.get_profile().get_badge()

        return super(ProfileView, self).get_context_data(**kwargs)
