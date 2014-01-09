#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation

from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.views.generic.detail import SingleObjectMixin


class ProfileView(TemplateView, SingleObjectMixin):
    model = User
    context_object_name = 'user' # name passed to template
    template_name = 'user_profile.html'

    def get_object(self, queryset=None):
        u = self.request.user
        return self.request.user

