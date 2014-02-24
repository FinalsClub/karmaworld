#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2012  FinalsClub Foundation

"""
    Models for the courses django app.
    Handles courses, and their related models
    Courses are the first class object, they contain notes.
    Courses have a manytoone relation to schools.
"""
import datetime
import reversion

from django.db import models
from django.utils.text import slugify
from django.core.urlresolvers import reverse
from karmaworld.settings.manual_unique_together import auto_add_check_unique_together


class SchoolManager(models.Manager):
    """ Handle restoring data. """
    def get_by_natural_key(self, usde_id):
        """
        Return a School defined by USDE number.
        """
        return self.get(usde_id=usde_id)


class School(models.Model):
    """ A grouping that contains many courses """
    objects     = SchoolManager()

    name        = models.CharField(max_length=255)
    slug        = models.SlugField(max_length=150, null=True)
    location    = models.CharField(max_length=255, blank=True, null=True)
    url         = models.URLField(max_length=511, blank=True)
    # Facebook keeps a unique identifier for all schools
    facebook_id = models.BigIntegerField(blank=True, null=True)
    # United States Department of Education institution_id
    usde_id     = models.BigIntegerField(blank=True, null=True, unique=True)
    file_count  = models.IntegerField(default=0)
    priority    = models.BooleanField(default=0)
    alias       = models.CharField(max_length=255, null=True, blank=True)
    hashtag     = models.CharField(max_length=16, null=True, blank=True, unique=True, help_text='School abbreviation without #')

    class Meta:
        """ Sort School by file_count descending, name abc=> """
        ordering = ['-file_count','-priority', 'name']

    def natural_key(self):
        """
        A School is uniquely defined by USDE number.

        Name should be unique, but there are some dupes in the DB.
        """
        return (self.usde_id,)

    def __unicode__(self):
        return u'School {0}: {1}'.format(self.usde_id, self.name)

    def save(self, *args, **kwargs):
        """ Save school and generate a slug if one doesn't exist """
        if not self.slug:
            self.slug = slugify(unicode(self.name))
        super(School, self).save(*args, **kwargs)

    @staticmethod
    def autocomplete_search_fields():
        return ("name__icontains",)

    def update_note_count(self):
        """ Update the School.file_count by summing the
            contained course.file_count
        """
        self.file_count = sum([course.file_count for course in self.course_set.all()])
        self.save()


class DepartmentManager(models.Manager):
    """ Handle restoring data. """
    def get_by_natural_key(self, name, school):
        """
        Return a Department defined by its name and school.
        """
        return self.get(name=name, school=school)


class Department(models.Model):
    """ Department within a School. """
    objects     = DepartmentManager()

    name        = models.CharField(max_length=255)
    school      = models.ForeignKey(School) # Should this be optional ever?
    slug        = models.SlugField(max_length=150, null=True)
    url         = models.URLField(max_length=511, blank=True, null=True)

    class Meta:
        """
        The same department name might exist across schools, but only once
        per school.
        """
        unique_together = ('name', 'school',)

    def __unicode__(self):
        return u'Department: {0} at {1}'.format(self.name, unicode(self.school))

    def natural_key(self):
        """
        A Department is uniquely defined by its school and name.
        """
        return (self.name, self.school.natural_key())
    # Requires School to be dumped first
    natural_key.dependencies = ['courses.school']

    def save(self, *args, **kwargs):
        """ Save department and generate a slug if one doesn't exist """
        if not self.slug:
            self.slug = slugify(unicode(self.name))
        super(Department, self).save(*args, **kwargs)


class ProfessorManager(models.Manager):
    """ Handle restoring data. """
    def get_by_natural_key(self, name, email):
        """
        Return a Professor defined by name and email address.
        """
        return self.get(name=name,email=email)


class Professor(models.Model):
    """
    Track professors for courses.
    """
    objects = ProfessorManager()

    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        """
        email should be unique, but some professors have no email address
        in the database. For those cases, the name must be appended for
        uniqueness.
        """
        unique_together = ('name', 'email',)

    def __unicode__(self):
        return u'Professor: {0} ({1})'.format(self.name, self.email)

    def natural_key(self):
        """
        A Professor is uniquely defined by his/her name and email.
        """
        return (self.name,self.email)


class ProfessorAffiliationManager(models.Manager):
    """ Handle restoring data. """
    def get_by_natural_key(self, prof, dept):
        """
        Return a ProfessorAffiliation defined by prof and department.
        """
        return self.get(professor=prof,department=dept)


class ProfessorAffiliation(models.Model):
    """
    Track professors for departments. (many-to-many)
    """
    objects    = ProfessorAffiliationManager()

    professor  = models.ForeignKey(Professor)
    department = models.ForeignKey(Department)

    def __unicode__(self):
        return u'Professor {0} working for {1}'.format(unicode(self.professor), unicode(self.department))

    class Meta:
        """
        Many-to-many across both professor and department.
        However, (prof, dept) as a tuple should only appear once.
        """
        unique_together = ('professor', 'department',)

    def natural_key(self):
        """
        A ProfessorAffiliation is uniquely defined by the prof and department
        """
        return (self.professor.natural_key(), self.department.natural_key())
    # Requires dependencies to be dumped first
    natural_key.dependencies = ['courses.professor','courses.department']


class CourseManager(models.Manager):
    """ Handle restoring data. """
    def get_by_natural_key(self, name, dept):
        """
        Return a Course defined by name and department.
        """
        return self.get(name=name,department=dept)


class Course(models.Model):
    """ First class object that contains many notes.Note objects """
    objects     = CourseManager()

    # Core metadata
    name        = models.CharField(max_length=255)
    slug        = models.SlugField(max_length=150, null=True)
    # department should remove nullable when school gets yoinked
    department  = models.ForeignKey(Department, blank=True, null=True)
    # school is an appendix: the kind that gets swollen and should be removed
    # (vistigial)
    school      = models.ForeignKey(School, null=True, blank=True)
    file_count  = models.IntegerField(default=0)

    desc        = models.TextField(max_length=511, blank=True, null=True)
    url         = models.URLField(max_length=511, blank=True, null=True)

    # instructor_* is vestigial, replaced by Professor+ProfessorTaught models.
    instructor_name     = models.CharField(max_length=255, blank=True, null=True)
    instructor_email    = models.EmailField(blank=True, null=True)

    updated_at      = models.DateTimeField(default=datetime.datetime.utcnow)

    created_at      = models.DateTimeField(auto_now_add=True)

    # Number of times this course has been flagged as abusive/spam.
    flags           = models.IntegerField(default=0,null=False)

    class Meta:
        ordering = ['-file_count', 'school', 'name']
        unique_together = ('name', 'department')
        unique_together = ('name', 'school')
        verbose_name = 'course'
        verbose_name_plural = 'courses'

    def __unicode__(self):
        return u"Course {0} in {1}".format(self.name, unicode(self.department))

    def natural_key(self):
        """
        A Course is uniquely defined by its name and the department it is in.
        """
        return (self.name, self.department.natural_key())
    # Requires dependencies to be dumped first
    natural_key.dependencies = ['courses.department']

    def get_absolute_url(self):
        """ return url based on urls.py definition. """
        return reverse('course_detail', kwargs={'slug':self.slug})

    def save(self, *args, **kwargs):
        """ Save school and generate a slug if one doesn't exist """
        super(Course, self).save(*args, **kwargs) # generate a self.id
        if not self.slug:
            self.set_slug()

    def get_updated_at_string(self):
        """ return the formatted style for datetime strings """
        return self.updated_at.strftime("%I%p // %a %b %d %Y")

    def set_slug(self):
        self.slug = slugify(u"%s %s" % (self.name, self.id))
        self.save() # Save the slug

    @staticmethod
    def autocomplete_search_fields():
        return ("name__icontains",)

    def update_note_count(self):
        """ Update self.file_count by summing the note_set """
        self.file_count = self.note_set.count()
        self.save()

reversion.register(Course)

class ProfessorTaughtManager(models.Manager):
    """ Handle restoring data. """
    def get_by_natural_key(self, prof, course):
        """
        Return a ProfessorTaught defined by professor and course.
        """
        return self.get(professor=prof, course=course)


class ProfessorTaught(models.Model):
    """
    Track professors teaching courses. (many-to-many)
    """
    objects   = ProfessorTaughtManager()

    professor = models.ForeignKey(Professor)
    course    = models.ForeignKey(Course)

    def __unicode__(self):
        return u'Professor {0} taught {1}'.format(unicode(self.professor), unicode(self.course))

    class Meta:
        # many-to-many across both fields,
        # but (prof, course) as a tuple should only appear once.
        unique_together = ('professor', 'course',)

    def natural_key(self):
        """
        A ProfessorTaught is uniquely defined by the prof and course.
        """
        return (self.professor.natural_key(), self.course.natural_key())
    # Requires dependencies to be dumped first
    natural_key.dependencies = ['courses.professor','courses.course']


# Enforce unique constraints even when we're using a database like
# SQLite that doesn't understand them
auto_add_check_unique_together(Course)
auto_add_check_unique_together(Department)
auto_add_check_unique_together(Professor)
auto_add_check_unique_together(ProfessorAffiliation)
auto_add_check_unique_together(ProfessorTaught)
