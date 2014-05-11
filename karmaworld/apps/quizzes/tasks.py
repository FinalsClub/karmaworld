#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation
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

logger = get_task_logger(__name__)

HIT_TITLE = 'Choose keywords and descriptions from course notes'
HIT_DESCRIPTION = "Read students' course notes on Karmanotes.org and " \
                  "identify 10 keywords along with descriptions of them"
HIT_OVERVIEW_TEMPLATE = \
        '<p>Go to the page at KarmaNotes.org by clicking the link provided below. ' \
        '<strong>Identify 10 key words (or short phrases) that are the most important to the document</strong> ' \
        'on the page. This requires reading and understanding the document. Write these words in the boxes below. ' \
        'Then, write definitions or descriptions of these keywords as they are provided in the page. ' \
        'If the page does not provide a definition or description, leave the box blank. ' \
        'For example, keywords might be &quot;John Locke,&quot; &quot;the Protestant reformation,&quot; ' \
        'or &quot;existentialism.&quot; Their respective definitions or descriptions might be &quot;life, ' \
        'liberty, and property,&quot; &quot;schism in Christianity started by Martin Luther,&quot; and ' \
        '&quot;existence precedes essence.&quot;</p>' \
        '<p>Notes link: <strong><a href="http://{domain}{link}">' \
        'http://{domain}{link}</a></strong></p>'
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
]

@task()
def submit_extract_keywords_hit(note):
    """Create a Mechanical Turk HIT that asks a worker to
    choose keywords and definitions from the given note."""

    try:
        from karmaworld.secret.mturk import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, MTURK_HOST
    except ImportError:
        logger.warn('Could not find Mechanical Turk secrets, not running submit_extract_keywords_hit')
        return

    connection = MTurkConnection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
                                 host=MTURK_HOST)

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
                                    is_required=True)
        question_form.append(keyword_question)

        definition_content = QuestionContent()
        definition_content.append_field('Title', DEFINITION_FIELDS[i][1])
        definition_question = Question(identifier=DEFINITION_FIELDS[i][0],
                                       content=definition_content,
                                       answer_spec=AnswerSpecification(definition_fta),
                                       is_required=False)
        question_form.append(definition_question)

    connection.create_hit(questions=question_form, max_assignments=1,
                          title=HIT_TITLE, description=HIT_DESCRIPTION,
                          keywords=HIT_KEYWORDS, duration=HIT_DURATION,
                          reward=HIT_REWARD, qualifications=HIT_QUALIFICATION,
                          annotation=str(note.id))


@task(name='get_extract_keywords_results')
def get_extract_keywords_results():

    try:
        from karmaworld.secret.mturk import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, MTURK_HOST
    except ImportError:
        logger.warn('Could not find Mechanical Turk secrets, not running get_extract_keywords_results')
        return

    connection = MTurkConnection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
                                 host=MTURK_HOST)

    reviewable_hits = connection.get_reviewable_hits(page_size=100)
    for hit in reviewable_hits:
        try:
            note_id = connection.get_hit(hit.HITId)[0].RequesterAnnotation
        except AttributeError:
            logger.error('HIT {0} does not have a RequesterAnnotation, '
                         'so we cannot determine which note it references'.format(hit.HITId))
            return

        try:
            note = Note.objects.get(id=note_id)
        except ObjectDoesNotExist:
            logger.error('Could not find note {0} which was referenced by HIT {1}'.format(note_id, hit.HITId))
            return

        answers = {}
        assignments = [a for a in connection.get_assignments(hit.HITId) if a.AssignmentStatus == 'Submitted']
        for assignment in assignments:
            for question_form_answer in assignment.answers[0]:
                answers[question_form_answer.qid] = question_form_answer.fields[0]

        for i in range(min(len(KEYWORD_FIELDS), len(DEFINITION_FIELDS))):
            keyword_qid = KEYWORD_FIELDS[i][0]
            definition_qid = DEFINITION_FIELDS[i][0]
            try:
                keyword = answers[keyword_qid]
                definition = answers[definition_qid]
                Keyword.objects.create(word=keyword, definition=definition, note=note, unreviewed=True)
            except KeyError:
                pass

        for assignment in assignments:
            connection.approve_assignment(assignment.AssignmentId)

        connection.dispose_hit(hit.HITId)
