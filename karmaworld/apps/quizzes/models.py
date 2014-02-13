#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2014  FinalsClub Foundation
import datetime
from django.db import models


class Keyword(models.Model):
    word = models.CharField(max_length=1024)
    definition = models.CharField(max_length=2048, blank=True, null=True)

    note = models.ForeignKey('notes.Note', blank=True, null=True)

    timestamp = models.DateTimeField(default=datetime.datetime.utcnow)

    class Meta:
        unique_together = ('word', 'note')

    def __unicode__(self):
        return self.word


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

    explanation = models.CharField(max_length=2048, blank=True, null=True)

    EASY = 'EASY'
    MEDIUM = 'MEDIUM'
    HARD = 'HARD'
    DIFFICULTY_CHOICES = (
        (EASY, 'Easy'),
        (MEDIUM, 'Medium'),
        (HARD, 'Hard'),
    )

    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES, blank=True, null=True)

    UNDERSTAND = 'UNDERSTAND'
    REMEMBER = 'REMEMBER'
    ANALYZE = 'ANALYZE'
    KNOWLEDGE = 'KNOWLEDGE'
    CATEGORY_CHOICES = (
        (UNDERSTAND, 'Understand'),
        (REMEMBER, 'Remember'),
        (ANALYZE, 'Analyze'),
        (KNOWLEDGE, 'Knowledge'),
    )

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True)


    class Meta:
        abstract = True


class MultipleChoiceQuestion(BaseQuizQuestion):
    question_text = models.CharField(max_length=2048)

    class Meta:
        verbose_name = 'Multiple choice question'

    def __unicode__(self):
        return self.question_text


class MultipleChoiceOption(models.Model):
    text = models.CharField(max_length=2048)
    correct = models.BooleanField()
    question = models.ForeignKey(MultipleChoiceQuestion, related_name="choices")

    def __unicode__(self):
        return self.text


class FlashCardQuestion(BaseQuizQuestion):
    sideA = models.CharField(max_length=2048, verbose_name='Side A')
    sideB = models.CharField(max_length=2048, verbose_name='Side B')

    class Meta:
        verbose_name = 'Flash card question'

    def __unicode__(self):
        return self.sideA + ' / ' + self.sideB


class TrueFalseQuestion(BaseQuizQuestion):
    text = models.CharField(max_length=2048)
    true = models.BooleanField(verbose_name='True?')

    class Meta:
        verbose_name = 'True/False question'

    def __unicode__(self):
        return self.text

ALL_QUESTION_CLASSES = (MultipleChoiceQuestion, FlashCardQuestion, TrueFalseQuestion)

