#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2014  FinalsClub Foundation
import datetime
from django.db import models


class Quiz(models.Model):
    name = models.CharField(max_length=512)
    note = models.ForeignKey('notes.Note', blank=True, null=True)
    timestamp = models.DateTimeField(default=datetime.datetime.utcnow)

    class Meta:
        verbose_name_plural = 'quizzes'

    def __unicode__(self):
        return self.name


class BaseQuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz)
    timestamp = models.DateTimeField(default=datetime.datetime.utcnow)

    class Meta:
        abstract = True


class MultipleChoiceQuestion(BaseQuizQuestion):
    question_text = models.CharField(max_length=2048)
    explanation = models.CharField(max_length=2048)

    EASY = 'EASY'
    MEDIUM = 'MEDIUM'
    HARD = 'HARD'
    DIFFICULTY_CHOICES = (
        (EASY, 'Easy'),
        (MEDIUM, 'Medium'),
        (HARD, 'Hard'),
    )

    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES)

    UNDERSTAND = 'UNDERSTAND'
    REMEMBER = 'REMEMBER'
    ANALYZE = 'ANALYZE'
    CATEGORY_CHOICES = (
        (UNDERSTAND, 'Understand'),
        (REMEMBER, 'Remember'),
        (ANALYZE, 'Analyze'),
    )

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    def __unicode__(self):
        return self.question_text


class MultipleChoiceOption(models.Model):
    text = models.CharField(max_length=2048)
    correct = models.BooleanField()
    question = models.ForeignKey(MultipleChoiceQuestion, related_name="choices")

    def __unicode__(self):
        return self.text


class FlashCardQuestion(BaseQuizQuestion):
    sideA = models.CharField(max_length=2048)
    sideB = models.CharField(max_length=2048)

    def __unicode__(self):
        return self.sideA + ' / ' + self.sideB

ALL_QUESTION_CLASSES = (MultipleChoiceQuestion, FlashCardQuestion)

