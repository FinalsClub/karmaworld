#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation
from django import forms


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=255, required=False, label='Given name')
    last_name  = forms.CharField(max_length=255, required=False, label='Family name')
    email      = forms.EmailField(label='Email address')

    def save(self, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        user.email      = self.cleaned_data['email']
        user.save()
