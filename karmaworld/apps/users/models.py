#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation
import random
import logging
from allauth.account.signals import user_logged_in, user_signed_up, email_confirmed, email_changed, email_added
from allauth.socialaccount.signals import pre_social_login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import models, DatabaseError
from django.middleware.transaction import transaction
from karmaworld.apps.courses.models import School

logger = logging.getLogger(__name__)

class UserProfile(models.Model):
    user      = models.OneToOneField(User)

    school    = models.ForeignKey(School, blank=True, null=True)

    karma     = models.IntegerField(default=0)

    def __unicode__(self):
        return self.user.__unicode__()

def user_display_name(user):
    """Return the best way to display a user's
    name to them on the site."""
    if hasattr(user, 'first_name') and user.first_name and \
            hasattr(user, 'last_name') and user.last_name:
        return user.first_name + ' ' + user.last_name
    elif hasattr(user, 'email') and user.email:
        return user.email
    else:
        return user.username

@receiver(post_save, sender=User, weak=True)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        with transaction.commit_on_success():
            try:
                UserProfile.objects.create(user=instance)
            except DatabaseError:
                logger.warn("Could not create UserProfile for user {u}. This is okay if running syncdb.".format(u=instance))

