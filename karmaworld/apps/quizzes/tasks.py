#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation
import os
from boto.mturk.qualification import PercentAssignmentsApprovedRequirement, Qualifications
from boto.mturk.question import Overview, FormattedContent, QuestionContent, Question, FreeTextAnswer, QuestionForm, \
    AnswerSpecification
from celery import task
from celery.utils.log import get_task_logger
from boto.mturk.connection import MTurkConnection
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from karmaworld.apps.notes.models import Note
from karmaworld.apps.quizzes.models import Keyword
from django.conf import settings

logger = get_task_logger(__name__)

HIT_TITLE_TEMPLATE = 'Get paid to learn {course} at {school}'
HIT_DESCRIPTION = "Read students' course notes on KarmaNotes.org and " \
                  "identify 10 or more keywords along with descriptions of them"
HIT_OVERVIEW_TEMPLATE = \
        '<p>KarmaNotes.org is a non-profit organization dedicated to free and open education. ' \
        'We need your help to identify keywords and definitions in college student lecture notes. ' \
        'Here is one example from an American History course:</p>' \
        '<p><strong>Constitutional Amendment</strong> &mdash; The process whereby the US ' \
        'Constitution may be altered by a two-thirds vote of the Senate and House of ' \
        'Representatives or a vote by at least two-thirds of the states.</p>' \
        '<p>In the notes below, please find keywords and definitions like the example above.</p>' \
        '<p>Notes link: <strong><a href="http://{domain}{link}">' \
        'http://{domain}{link}</a></strong></p>' \
        '<p>In these notes, please find 10 to 20 key words and definitions within these student notes. ' \
        'With your help, we will generate free and open flashcards and quizzes to help ' \
        'students study.  Together we can open education, one lecture at a time.</p>'
HIT_KEYWORDS = 'writing, summary, keywords'
HIT_DURATION = 60 * 60 * 24 * 7
HIT_REWARD = 0.92
HIT_PERCENT_APPROVED_REQUIREMENT = PercentAssignmentsApprovedRequirement(comparator='GreaterThan', integer_value=95)
HIT_QUALIFICATION = Qualifications(requirements=[HIT_PERCENT_APPROVED_REQUIREMENT])

KEYWORD_FIELDS = [
    ('keyword01', 'Keyword 1'),
    ('keyword02', 'Keyword 2'),
    ('keyword03', 'Keyword 3'),
    ('keyword04', 'Keyword 4'),
    ('keyword05', 'Keyword 5'),
    ('keyword06', 'Keyword 6'),
    ('keyword07', 'Keyword 7'),
    ('keyword08', 'Keyword 8'),
    ('keyword09', 'Keyword 9'),
    ('keyword10', 'Keyword 10'),
    ('keyword11', 'Keyword 11'),
    ('keyword12', 'Keyword 12'),
    ('keyword13', 'Keyword 13'),
    ('keyword14', 'Keyword 14'),
    ('keyword15', 'Keyword 15'),
    ('keyword16', 'Keyword 16'),
    ('keyword17', 'Keyword 17'),
    ('keyword18', 'Keyword 18'),
    ('keyword19', 'Keyword 19'),
    ('keyword20', 'Keyword 20'),
]

DEFINITION_FIELDS = [
    ('definition01', 'Definition 1'),
    ('definition02', 'Definition 2'),
    ('definition03', 'Definition 3'),
    ('definition04', 'Definition 4'),
    ('definition05', 'Definition 5'),
    ('definition06', 'Definition 6'),
    ('definition07', 'Definition 7'),
    ('definition08', 'Definition 8'),
    ('definition09', 'Definition 9'),
    ('definition10', 'Definition 10'),
    ('definition11', 'Definition 11'),
    ('definition12', 'Definition 12'),
    ('definition13', 'Definition 13'),
    ('definition14', 'Definition 14'),
    ('definition15', 'Definition 15'),
    ('definition16', 'Definition 16'),
    ('definition17', 'Definition 17'),
    ('definition18', 'Definition 18'),
    ('definition19', 'Definition 19'),
    ('definition20', 'Definition 20'),
]

@task(name='submit_extract_keywords_hit')
def submit_extract_keywords_hit(note):
    """Create a Mechanical Turk HIT that asks a worker to
    choose keywords and definitions from the given note."""

    try:
        MTURK_HOST = os.environ['MTURK_HOST']
    except:
        logger.warn('Could not find Mechanical Turk secrets, not running submit_extract_keywords_hit')
        return

    connection = MTurkConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY,
                                 host=MTURK_HOST)

    if note.course.school:
        title = HIT_TITLE_TEMPLATE.format(course=note.course.name, school=note.course.school.name)
    else:
        title = HIT_TITLE_TEMPLATE.format(course=note.course.name, school=note.course.department.school.name)

    overview = Overview()
    overview.append(FormattedContent(HIT_OVERVIEW_TEMPLATE.format(domain=Site.objects.get_current(),
                                                                  link=note.get_absolute_url())))

    keyword_fta = FreeTextAnswer()
    keyword_fta.num_lines = 1

    definition_fta = FreeTextAnswer()
    definition_fta.num_lines = 3

    question_form = QuestionForm()
    question_form.append(overview)

    for i in range(min(len(KEYWORD_FIELDS), len(DEFINITION_FIELDS))):
        keyword_content = QuestionContent()
        keyword_content.append_field('Title', KEYWORD_FIELDS[i][1])
        keyword_question = Question(identifier=KEYWORD_FIELDS[i][0],
                                    content=keyword_content,
                                    answer_spec=AnswerSpecification(keyword_fta),
                                    is_required=True if i <= 10 else False)
        question_form.append(keyword_question)

        definition_content = QuestionContent()
        definition_content.append_field('Title', DEFINITION_FIELDS[i][1])
        definition_question = Question(identifier=DEFINITION_FIELDS[i][0],
                                       content=definition_content,
                                       answer_spec=AnswerSpecification(definition_fta),
                                       is_required=False)
        question_form.append(definition_question)

    connection.create_hit(questions=question_form, max_assignments=1,
                          title=title, description=HIT_DESCRIPTION,
                          keywords=HIT_KEYWORDS, duration=HIT_DURATION,
                          reward=HIT_REWARD, qualifications=HIT_QUALIFICATION,
                          annotation=str(note.id))


@task(name='get_extract_keywords_results')
def get_extract_keywords_results():

    try:
        MTURK_HOST = os.environ['MTURK_HOST']
    except ImportError:
        logger.warn('Could not find Mechanical Turk secrets, not running get_extract_keywords_results')
        return

    connection = MTurkConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY,
                                 host=MTURK_HOST)

    reviewable_hits = connection.get_reviewable_hits(status='Reviewable', page_size=100,
                                                     sort_by='CreationTime', sort_direction='Descending')
    for hit in reviewable_hits:
        logger.info('Found HIT {0}'.format(hit.HITId))
        try:
            note_id = connection.get_hit(hit.HITId)[0].RequesterAnnotation
            note_id = int(note_id)
        except (AttributeError, ValueError):
            logger.error('HIT {0} does not have a valid RequesterAnnotation, '
                         'so we cannot determine which note it references'.format(hit.HITId))
            return

        try:
            note = Note.objects.get(id=note_id)
        except ObjectDoesNotExist:
            logger.error('Could not find note {0} which was referenced by HIT {1}'.format(note_id, hit.HITId))
            return

        answers = {}
        assignments = [a for a in connection.get_assignments(hit.HITId) if a.AssignmentStatus == 'Approved']
        for assignment in assignments:
            for question_form_answer in assignment.answers[0]:
                answers[question_form_answer.qid] = question_form_answer.fields[0]

        for i in range(min(len(KEYWORD_FIELDS), len(DEFINITION_FIELDS))):
            keyword_qid = KEYWORD_FIELDS[i][0]
            definition_qid = DEFINITION_FIELDS[i][0]
            try:
                keyword = answers[keyword_qid]
                definition = answers[definition_qid]
                if keyword:
                    Keyword.objects.create(word=keyword, definition=definition, note=note, unreviewed=True)
            except KeyError:
                pass
