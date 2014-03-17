#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2014  FinalsClub Foundation
from itertools import chain
import json
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotFound, HttpResponse

from django.views.generic import DetailView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin, ProcessFormView
from karmaworld.apps.notes.models import Note
from karmaworld.apps.quizzes.forms import KeywordForm
from karmaworld.apps.quizzes.models import Quiz, ALL_QUESTION_CLASSES, Keyword, BaseQuizQuestion, \
    ALL_QUESTION_CLASSES_NAMES, MultipleChoiceQuestion, MultipleChoiceOption, TrueFalseQuestion, FlashCardQuestion
from karmaworld.utils import ajax_base


class QuizView(DetailView):
    queryset = Quiz.objects.all()
    model = Quiz
    context_object_name = 'quiz'  # name passed to template
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
        kwargs['quiz'] = self.object

        return super(QuizView, self).get_context_data(**kwargs)


class KeywordEditView(FormView):
    template_name = 'quizzes/keyword_edit.html'
    form_class = formset_factory(KeywordForm)

    def get(self, requests, *args, **kwargs):
        self.lookup_note()
        return super(KeywordEditView, self).get(requests, *args, **kwargs)

    def post(self, requests, *args, **kwargs):
        self.lookup_note()
        return super(KeywordEditView, self).post(requests, *args, **kwargs)

    def lookup_note(self):
        self.note = Note.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self):
        return reverse('keyword_edit', args=(self.note.course.school.slug, self.note.course.slug, self.note.slug))

    def get_initial(self):
        existing_keywords = self.note.keyword_set.order_by('id')
        initial_data = [{'keyword': keyword.word, 'definition': keyword.definition, 'id': keyword.pk}
                        for keyword in existing_keywords]
        return initial_data

    def get_context_data(self, **kwargs):
        kwargs['note'] = self.note
        kwargs['prototype_form'] = KeywordForm
        return super(KeywordEditView, self).get_context_data(**kwargs)

    def form_valid(self, formset):
        for form in formset:
            word = form['keyword'].data
            definition = form['definition'].data
            id = form['id'].data
            if word == '':
                continue
            try:
                keyword_object = Keyword.objects.get(id=id)
            except (ValueError, ObjectDoesNotExist):
                keyword_object = Keyword()

            keyword_object.note = self.note
            keyword_object.word = word
            keyword_object.definition = definition
            keyword_object.save()

        return super(KeywordEditView, self).form_valid(formset)


def quiz_answer(request):
    """Handle an AJAX request checking if a quiz answer is correct"""
    if not (request.method == 'POST' and request.is_ajax()):
        # return that the api call failed
        return HttpResponseBadRequest(json.dumps({'status': 'fail', 'message': 'must be a POST ajax request'}),
                                      mimetype="application/json")

    try:
        question_type_str = request.POST['question_type']
        if question_type_str not in ALL_QUESTION_CLASSES_NAMES:
            raise Exception("Not a valid question type")
        question_type_class = ALL_QUESTION_CLASSES_NAMES[question_type_str]
        question = question_type_class.objects.get(id=request.POST['id'])

        correct = False

        if question_type_class is MultipleChoiceQuestion:
            answer = MultipleChoiceOption.objects.get(id=request.POST['answer'])
            if answer.question == question and answer.correct:
                correct = True

        elif question_type_class is TrueFalseQuestion:
            answer = request.POST['answer'] == 'true'
            correct = question.true == answer

        elif question_type_class is FlashCardQuestion:
            answer = request.POST['answer'].lower()
            correct = question.keyword_side.lower() == answer

    except Exception, e:
        return HttpResponseBadRequest(json.dumps({'status': 'fail',
                                                  'message': e.message,
                                                  'exception': e.__class__.__name__}),
                                      mimetype="application/json")

    return HttpResponse(json.dumps({'correct': correct}), mimetype="application/json")