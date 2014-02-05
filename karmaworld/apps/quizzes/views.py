#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2014  FinalsClub Foundation
from itertools import chain

from django.views.generic import TemplateView, DetailView
from django.views.generic.detail import SingleObjectMixin
from karmaworld.apps.quizzes.models import Quiz, ALL_QUESTION_CLASSES


class QuizView(DetailView):

    queryset = Quiz.objects.all()

    model = Quiz
    context_object_name = 'quiz' # name passed to template
    template_name = 'quizzes/quiz.html'

    def get_context_data(self, **kwargs):
        all_questions = []
        for cls in ALL_QUESTION_CLASSES:
            all_questions.append(
                [(cls.__name__, o) for o in cls.objects.filter(quiz=self.object)]
            )

        result_list = sorted(chain.from_iterable(all_questions),
                             key=lambda o: o[1].timestamp,
                             reverse=True)

        kwargs['questions'] = result_list

        return super(QuizView, self).get_context_data(**kwargs)

