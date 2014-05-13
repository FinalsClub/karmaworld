#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation
import logging
import datetime
from allauth.account.signals import email_confirmed
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models, DatabaseError
from django.middleware.transaction import transaction
from karmaworld.apps.courses.models import School

logger = logging.getLogger(__name__)


class UserProfileManager(models.Manager):
    """ Handle restoring data. """
    def get_by_natural_key(self, user):
        return self.get(user=user)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    thanked_notes = models.ManyToManyField('notes.Note', related_name='users_thanked', blank=True, null=True)
    flagged_notes = models.ManyToManyField('notes.Note', related_name='users_flagged', blank=True, null=True)
    flagged_courses = models.ManyToManyField('courses.Course', related_name='users_flagged', blank=True, null=True)
    school = models.ForeignKey(School, blank=True, null=True)

    def natural_key(self):
        return (self.user,)

    def get_points(self):
        sum = 0
        for cls in ALL_KARMA_EVENT_CLASSES:
            points = cls.objects.filter(user=self.user).aggregate(Sum('points'))['points__sum']
            if points:
                sum += points

        return sum

    def can_edit_items(self):
        if self.user.is_staff:
            return True
        else:
            return (self.get_points() >= 20)

    NO_BADGE = 0
    PROSPECT = 1
    BEGINNER = 2
    TRAINEE = 3
    APPRENTICE = 4
    SCHOLAR = 5

    BADGES = (
        PROSPECT,
        BEGINNER,
        TRAINEE,
        APPRENTICE,
        SCHOLAR
    )

    BADGE_NAMES = {
        PROSPECT: 'Prospect',
        BEGINNER: 'Beginner',
        TRAINEE: 'Trainee',
        APPRENTICE: 'Apprentice',
        SCHOLAR: 'Scholar'
    }

    BADGE_THRESHOLDS = {
        PROSPECT: 10,
        BEGINNER: 100,
        TRAINEE: 200,
        APPRENTICE: 500,
        SCHOLAR: 1000
    }

    def get_badge(self):
        points = self.get_points()
        highest_badge = self.NO_BADGE
        for badge in self.BADGES:
            if points >= self.BADGE_THRESHOLDS[badge]:
                highest_badge = badge

        if highest_badge is not self.NO_BADGE:
            return self.BADGE_NAMES[highest_badge]
        else:
            return None

    def __unicode__(self):
        return self.user.__unicode__()


@receiver(email_confirmed, weak=True)
def give_email_confirm_karma(sender, **kwargs):
    GenericKarmaEvent.create_event(kwargs['email_address'].user, kwargs['email_address'].email, GenericKarmaEvent.EMAIL_CONFIRMED)


class BaseKarmaEventManager(models.Manager):
    """ Handle restoring data. """
    def get_by_natural_key(self, points, user, timestamp):
        return self.get(user=user, timestamp=timestamp)


class BaseKarmaEvent(models.Model):
    points    = models.IntegerField()
    user      = models.ForeignKey(User)
    timestamp = models.DateTimeField(default=datetime.datetime.utcnow)

    class Meta:
        abstract = True
        unique_together = ('points', 'user', 'timestamp')

    def natural_key(self):
        return (self.user, self.timestamp)

    def get_message(self):
        raise NotImplemented()


class GenericKarmaEvent(BaseKarmaEvent):
    NONE = 'none'
    NOTE_DELETED       = 'upload'
    EMAIL_CONFIRMED    = 'thanks'

    EVENT_TYPE_CHOICES = (
        (NONE,               'This should not happen'),
        (NOTE_DELETED,       'Your note "{m}" was deleted'),
        (EMAIL_CONFIRMED,    'You confirmed your email address {m}'),
    )

    POINTS = {
        NOTE_DELETED: -5,
        EMAIL_CONFIRMED: 5,
    }

    event_type = models.CharField(max_length=15, choices=EVENT_TYPE_CHOICES, default=NONE)
    message = models.CharField(max_length=255)

    @staticmethod
    def create_event(user, message, type):
        event = GenericKarmaEvent.objects.create(user=user,
                                                 points=GenericKarmaEvent.POINTS[type],
                                                 event_type=type,
                                                 message=message)
        event.save()

    def get_message(self):
        if self.event_type == self.NONE:
            return self.message
        else:
            return self.get_event_type_display().format(m=self.message)

    def __unicode__(self):
        return unicode(self.user) + ' -- ' + self.get_message()


class NoteKarmaEvent(BaseKarmaEvent):
    UPLOAD       = 'upload'
    THANKS       = 'thanks'
    NOTE_DELETED = 'deleted'
    GIVE_FLAG    = 'give_flag'
    GET_FLAGGED  = 'get_flagged'
    DOWNLOADED_NOTE = 'downloaded'
    HAD_NOTE_DOWNLOADED = 'was_downloaded'
    CREATED_KEYWORD = 'created_keyword'

    EVENT_TYPE_CHOICES = (
        (UPLOAD,       "You uploaded a note"),
        (THANKS,       "You received a thanks for your note"),
        (NOTE_DELETED, "Your note was deleted"),
        (GIVE_FLAG,    "You flagged a note"),
        (GET_FLAGGED,  "Your note was flagged as spam"),
        (DOWNLOADED_NOTE,  "You downloaded a note"),
        (HAD_NOTE_DOWNLOADED,  "Your note was downloaded"),
        (CREATED_KEYWORD,  "You created a keyword"),
    )
    note = models.ForeignKey('notes.Note')
    event_type = models.CharField(max_length=15, choices=EVENT_TYPE_CHOICES)

    POINTS = {
        UPLOAD: 5,
        THANKS: 1,
        NOTE_DELETED: -5,
        GIVE_FLAG: -1,
        GET_FLAGGED: -100,
        DOWNLOADED_NOTE: -2,
        HAD_NOTE_DOWNLOADED: 2,
        CREATED_KEYWORD: 1,
    }

    def get_message(self):
        return self.get_event_type_display()

    def __unicode__(self):
        return unicode(self.user) + ' -- ' + self.get_event_type_display() + ' -- ' + unicode(self.note)

    @staticmethod
    def create_event(user, note, type):
        event = NoteKarmaEvent.objects.create(user=user,
                                      note=note,
                                      points=NoteKarmaEvent.POINTS[type],
                                      event_type=type)
        event.save()


class CourseKarmaEvent(BaseKarmaEvent):
    GIVE_FLAG    = 'give_flag'
    EVENT_TYPE_CHOICES = (
        (GIVE_FLAG,    "You flagged a course"),
    )
    course = models.ForeignKey('courses.Course')
    event_type = models.CharField(max_length=15, choices=EVENT_TYPE_CHOICES)

    POINTS = {
        GIVE_FLAG: -1,
    }

    def get_message(self):
        return self.get_event_type_display()

    def __unicode__(self):
        return unicode(self.user) + ' -- ' + self.get_event_type_display() + ' -- ' + unicode(self.course)

    @staticmethod
    def create_event(user, course, type):
        event = CourseKarmaEvent.objects.create(user=user,
                                      course=course,
                                      points=CourseKarmaEvent.POINTS[type],
                                      event_type=type)
        event.save()


ALL_KARMA_EVENT_CLASSES = (GenericKarmaEvent, NoteKarmaEvent, CourseKarmaEvent)


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

