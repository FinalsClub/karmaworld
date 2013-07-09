#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation
""" A script to sanitize the imported USDE database.
    It will remove schools who's name contains words
    in the RESTRICTED_WORDS list """

from django.core.management.base import BaseCommand
from django.db.models import Q

from karmaworld.apps.courses.models import School

RESTRICTED_WORDS = [
                'internship',
                'dietetic',
                'massage',
                'therapy',
                'residency',
                'months',
                'hair',
                'cosmetology',
                'beauty',
                'nail',
                'acupuncture',
                'chiropractic']


class Command(BaseCommand):
    """ Delete Schools that contain RESTRICTED WORDS in their names """
    args = 'none'
    help = """ Delete Schools that contain RESTRICTED WORDS in their names """

    def get_input(self, input_prompt):
        """ Get user input with repeated requests on incorrect input """

        y_n = raw_input(input_prompt)
        y_n = y_n.replace(" ", "") # strip extra spaces
        y_n = y_n.lower()

        if y_n == 'y':
            return True
        elif y_n == 'n':
            return False
        else:
            error_prompt = "Valid responses are [yYnN]\n"
            return self.get_input(error_prompt + input_prompt)


    def handle(self, *args, **kwargs):
        """ The function that gets called to run this command """
        # generate an |(or)'d list of queries searching inexact for each of RESTRICTED_WORDS
        queries_list    = map(lambda word: Q(name__icontains=word), RESTRICTED_WORDS)
        queries_or      = reduce(lambda a, b: a | b, queries_list)
        schools = School.objects.filter(queries_or)
        self._schools_count = schools.count()

        # if there are no schools, exit
        if not self._schools_count:
            self.stdout.write('\n')
            self.stdout.write('There are no schools worth sanitizing.\n')
            return False

        self.stdout.write(u"\n\nWARNING: Are you sure you want to delete these schools:\n")
        for s in schools:
            self.stdout.write('%s: %s' % (s.id, s.__unicode__()))
            self.stdout.write('\n')

        if self.get_input("Do you want to delete these schools? [y/n]  "):
            self.stdout.write("...")
            try:
                schools.delete()
            except:
                self.stdout.write("that is too many to delete at once\n")
                self.stdout.write("you are probabily using sqlite , doing them in batches\n")
                for _i, a_school in enumerate(schools):
                    self.stdout.write("deleting %s of %s..." % (_i, self._schools_count))
                    a_school.delete()
                    self.stdout.write("done\n")
                self.stdout.write("...")

            self.stdout.write("all done!\n")
            self.stdout.write("Deleted %s schools" % (self._schools_count))
