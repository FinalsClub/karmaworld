#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

from django.core.management.base import BaseCommand
from apps.notes.models import Note

class Command(BaseCommand):
    args = 'none'
    help = "regenerate all note slugs"

    def handle(self, *args, **kwargs):
        notes = Note.objects.fall()
        for n in notes:
            n.slug = None
            n.save()

