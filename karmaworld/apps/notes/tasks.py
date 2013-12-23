#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation

from celery import task
from karmaworld.apps.notes.models import Note
from karmaworld.secret.twitter import *
import twitter
import logging
from pyshorteners.shorteners import Shortener

logger = logging.getLogger(__name__)

@task(name="tweet_note")
def tweet_note():
    """Tweet about a new note."""

    api = twitter.Api(consumer_key=CONSUMER_KEY,
                      consumer_secret=CONSUMER_SECRET,
                      access_token_key=ACCESS_TOKEN_KEY,
                      access_token_secret=ACCESS_TOKEN_SECRET)

    newest_notes = Note.objects.all()[:100]
    for n in newest_notes:
        if not n.tweeted:
            update = tweet_string(n)
            logger.info("Tweeting:")
            logger.info(update)

            # Mark this tweeted before we actually tweet it
            # to be extra safe against double tweets
            n.tweeted = True
            n.save()

            api.PostUpdate(tweet_string(n))

            break


def tweet_string(note):
    # This url will use 13 characters
    shortener = Shortener('GoogleShortener')
    url = "https://www.karmanotes.org" + \
        note.get_absolute_url()
    short_url = shortener.short(url)

    # space character

    # 16 characters
    school = note.course.school.slug
    short_school = school[:school.find('-')][:16]

    # space character

    # 50 characters
    short_course = note.course.name[:50]

    # space and colon characters

    # 57 characters
    short_note = note.name[:57]

    return short_url + " #" + short_school + " " + \
        short_course + ": " + \
        short_note

