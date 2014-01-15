#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation
import random
import logging
from allauth.account.signals import user_logged_in
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
    if user.first_name or user.last_name:
        return user.first_name + ' ' + user.last_name
    else:
        return user.username


@receiver(pre_save, sender=User, weak=True)
def assign_username(sender, instance, **kwargs):
    # If a user does not have a username, they need
    # one before we save to the database
    if not instance.username:
        if instance.email:
            try:
                # See if any other users have this email address
                others = User.objects.get(email=instance.email)
            except ObjectDoesNotExist:
                instance.username = instance.email
            else:
                instance.username = 'user' + str(random.randint(10000, 100000))
        else:
            instance.username = 'user' + str(random.randint(10000, 100000))


@receiver(post_save, sender=User, weak=True)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        with transaction.commit_on_success():
            try:
                UserProfile.objects.create(user=instance)
            except DatabaseError:
                logger.warn("Could not create UserProfile for user {u}. This is okay if running syncdb.".format(u=instance))

