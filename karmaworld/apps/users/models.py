#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation
import logging
import datetime
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models, DatabaseError
from django.middleware.transaction import transaction
from karmaworld.apps.courses.models import School

logger = logging.getLogger(__name__)


class UserProfile(models.Model):
    user      = models.OneToOneField(User)

    school    = models.ForeignKey(School, blank=True, null=True)

    def get_points(self):
        sum = 0
        for cls in ALL_KARMA_EVENT_CLASSES:
            points = cls.objects.filter(user=self.user).aggregate(Sum('points'))['points__sum']
            if points:
                sum += points

        return sum

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
        return highest_badge

    def __unicode__(self):
        return self.user.__unicode__()


class BaseKarmaEvent(models.Model):
    points    = models.IntegerField()
    user      = models.ForeignKey(User)
    timestamp = models.DateTimeField(default=datetime.datetime.utcnow)

    class Meta:
        abstract = True

    def get_message(self):
        raise NotImplemented()


class GenericKarmaEvent(BaseKarmaEvent):
    message = models.CharField(max_length=255)

    @staticmethod
    def create_event(user, message, points):
        event = GenericKarmaEvent.objects.create(user=user,
                                                 points=points,
                                                 message=message)
        event.save()

    def get_message(self):
        return self.message


class NoteKarmaEvent(BaseKarmaEvent):
    UPLOAD       = 'upload'
    THANKS       = 'thanks'
    NOTE_DELETED = 'deleted'
    GIVE_FLAG    = 'give_flag'
    GET_FLAGGED  = 'get_flagged'
    EVENT_TYPE_CHOICES = (
        (UPLOAD,       "You uploaded a note"),
        (THANKS,       "You received a thanks for your note"),
        (NOTE_DELETED, "Your note was deleted"),
        (GIVE_FLAG,    "You flagged a note"),
        (GET_FLAGGED,  "Your note was flagged as spam"),
    )
    note = models.ForeignKey('notes.Note')
    event_type = models.CharField(max_length=15, choices=EVENT_TYPE_CHOICES)

    POINTS = {
        UPLOAD: 5,
        THANKS: 1,
        NOTE_DELETED: -5,
        GIVE_FLAG: -1,
        GET_FLAGGED: -100
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

