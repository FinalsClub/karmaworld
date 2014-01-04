#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation

import traceback
from celery import task
from celery.utils.log import get_task_logger
from karmaworld.apps.notes.models import Note
import twitter
import gdshortener

logger = get_task_logger(__name__)

@task(name="tweet_note")
def tweet_note():
    """Tweet about a new note."""

    try:
        import karmaworld.secret.twitter as secrets
    except ImportError:
        logger.warn("No twitter secrets found, not running tweet_note")
        return

    try:
        api = twitter.Api(consumer_key=secrets.CONSUMER_KEY,
                          consumer_secret=secrets.CONSUMER_SECRET,
                          access_token_key=secrets.ACCESS_TOKEN_KEY,
                          access_token_secret=secrets.ACCESS_TOKEN_SECRET)

        newest_notes = Note.objects.all().order_by('-uploaded_at')[:100]
        for n in newest_notes:
            if not n.tweeted:
                update = tweet_string(n)
                logger.info("Tweeting: " + update)

                # Mark this tweeted before we actually tweet it
                # to be extra safe against double tweets
                n.tweeted = True
                n.save()

                api.PostUpdate(tweet_string(n))

                break
    except:
        logger.error(traceback.format_exc())


def tweet_string(note):
    # This url will use 13 or less characters
    shortener = gdshortener.ISGDShortener()
    url = "http://www.karmanotes.org" + \
        note.get_absolute_url()
    short_url = shortener.shorten(url)[0]

    # 50 characters
    short_course = note.course.name[:50]

    # 57 characters
    short_note = note.name[:57]

    if note.course.school.hashtag:
        return short_url + " #" + note.course.school.hashtag + " " + \
        short_course + ": " + \
        short_note
    else:
        return short_url + " " + \
            short_course + ": " + \
            short_note
