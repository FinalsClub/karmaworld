#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2014  FinalsClub Foundation
from django.contrib import admin
from nested_inlines.admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline
from karmaworld.apps.quizzes.models import MultipleChoiceQuestion, FlashCardQuestion, MultipleChoiceOption, Quiz


class MultipleChoiceOptionInlineAdmin(NestedTabularInline):
    model = MultipleChoiceOption


class MultipleChoiceQuestionAdmin(NestedModelAdmin):
    model = MultipleChoiceQuestion
    inlines = [MultipleChoiceOptionInlineAdmin,]
    list_display = ('question_text', 'quiz')


class MultipleChoiceQuestionInlineAdmin(NestedStackedInline):
    model = MultipleChoiceQuestion
    inlines = [MultipleChoiceOptionInlineAdmin,]
    list_display = ('question_text', 'quiz')


class FlashCardQuestionInlineAdmin(NestedStackedInline):
    model = FlashCardQuestion
    list_display = ('sideA', 'sideB', 'quiz')


class QuizAdmin(NestedModelAdmin):
    #search_fields = ['name', 'note__name']
    #list_display = ('name', 'note')
    inlines = [MultipleChoiceQuestionInlineAdmin, FlashCardQuestionInlineAdmin]


admin.site.register(Quiz, QuizAdmin)
admin.site.register(MultipleChoiceQuestion, MultipleChoiceQuestionAdmin)
admin.site.register(MultipleChoiceOption)
admin.site.register(FlashCardQuestion)
