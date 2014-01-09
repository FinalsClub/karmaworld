#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation
from allauth.account.signals import user_logged_in
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from karmaworld.apps.courses.models import School


class UserProfile(models.Model):
    user      = models.OneToOneField(User)

    school    = models.ForeignKey(School, blank=True, null=True)

    karma     = models.IntegerField(default=0)

    def __unicode__(self):
        return self.user.__unicode__()


@receiver(post_save, sender=User, weak=True)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

