#!/usr/bin/env python
# -*- coding:utf8 -*-
# Copyright (C) 2013  FinalsClub Foundation
import email
import poplib
import base64
import re
import time
import json
from karmaworld.utils.filepicker import encode_fp_policy, sign_fp_policy
import os
from boto.mturk.qualification import PercentAssignmentsApprovedRequirement, Qualifications
from boto.mturk.question import Overview, FormattedContent, QuestionContent, Question, FreeTextAnswer, QuestionForm, \
    AnswerSpecification, SelectionAnswer
from celery import task
from celery.utils.log import get_task_logger
from boto.mturk.connection import MTurkConnection
from django.contrib.sites.models import Site
from karmaworld.apps.notes.models import Document
from karmaworld.apps.quizzes.models import Keyword, HIT
from django.conf import settings
import requests


logger = get_task_logger(__name__)

KEYWORDS_HIT_TITLE_TEMPLATE = 'Get paid to learn {course} at {school}'
KEYWORDS_HIT_DESCRIPTION = "Read students' course notes on KarmaNotes.org and " \
                  "identify 10 or more keywords along with descriptions of them"
KEYWORDS_HIT_OVERVIEW_TEMPLATE = \
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
KEYWORDS_HIT_KEYWORDS = 'writing, summary, keywords'
KEYWORDS_HIT_DURATION = 60 * 60 * 24 * 7
KEYWORDS_HIT_REWARD = 0.92
KEYWORDS_HIT_PERCENT_APPROVED_REQUIREMENT = PercentAssignmentsApprovedRequirement(comparator='GreaterThan', integer_value=95)
KEYWORDS_HIT_QUALIFICATION = Qualifications(requirements=[KEYWORDS_HIT_PERCENT_APPROVED_REQUIREMENT])

KEYWORDS_HIT_KEYWORD_FIELDS = [
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

KEYWORDS_HIT_DEFINITION_FIELDS = [
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
        title = KEYWORDS_HIT_TITLE_TEMPLATE.format(course=note.course.name, school=note.course.school.name)
    else:
        title = KEYWORDS_HIT_TITLE_TEMPLATE.format(course=note.course.name, school=note.course.department.school.name)

    overview = Overview()
    overview.append(FormattedContent(KEYWORDS_HIT_OVERVIEW_TEMPLATE.format(domain=Site.objects.get_current(),
                                                                  link=note.get_absolute_url())))

    keyword_fta = FreeTextAnswer()
    keyword_fta.num_lines = 1

    definition_fta = FreeTextAnswer()
    definition_fta.num_lines = 3

    question_form = QuestionForm()
    question_form.append(overview)

    for i in range(min(len(KEYWORDS_HIT_KEYWORD_FIELDS), len(KEYWORDS_HIT_DEFINITION_FIELDS))):
        keyword_content = QuestionContent()
        keyword_content.append_field('Title', KEYWORDS_HIT_KEYWORD_FIELDS[i][1])
        keyword_question = Question(identifier=KEYWORDS_HIT_KEYWORD_FIELDS[i][0],
                                    content=keyword_content,
                                    answer_spec=AnswerSpecification(keyword_fta),
                                    is_required=True if i <= 10 else False)
        question_form.append(keyword_question)

        definition_content = QuestionContent()
        definition_content.append_field('Title', KEYWORDS_HIT_DEFINITION_FIELDS[i][1])
        definition_question = Question(identifier=KEYWORDS_HIT_DEFINITION_FIELDS[i][0],
                                       content=definition_content,
                                       answer_spec=AnswerSpecification(definition_fta),
                                       is_required=False)
        question_form.append(definition_question)

    hit = connection.create_hit(questions=question_form, max_assignments=1,
                          title=title, description=KEYWORDS_HIT_DESCRIPTION,
                          keywords=KEYWORDS_HIT_KEYWORDS, duration=KEYWORDS_HIT_DURATION,
                          reward=KEYWORDS_HIT_REWARD, qualifications=KEYWORDS_HIT_QUALIFICATION,
                          annotation=str(note.id))[0]

    HIT.objects.create(HITId=hit.HITId, note=note, processed=False)



@task(name='get_extract_keywords_results')
def get_extract_keywords_results():

    try:
        MTURK_HOST = os.environ['MTURK_HOST']
    except ImportError:
        logger.warn('Could not find Mechanical Turk secrets, not running get_extract_keywords_results')
        return

    connection = MTurkConnection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY,
                                 host=MTURK_HOST)

    for hit_object in HIT.objects.filter(processed=False):
        logger.info('Found unprocessed HIT {0}'.format(hit_object.HITId))

        answers = {}
        assignments = [a for a in connection.get_assignments(hit_object.HITId) if a.AssignmentStatus == 'Approved']
        for assignment in assignments:
            logger.info('Found approved assignment for HIT {0}'.format(hit_object.HITId))
            for question_form_answer in assignment.answers[0]:
                answers[question_form_answer.qid] = question_form_answer.fields[0]

        for i in range(min(len(KEYWORDS_HIT_KEYWORD_FIELDS), len(KEYWORDS_HIT_DEFINITION_FIELDS))):
            keyword_qid = KEYWORDS_HIT_KEYWORD_FIELDS[i][0]
            definition_qid = KEYWORDS_HIT_DEFINITION_FIELDS[i][0]
            try:
                keyword = answers[keyword_qid]
                definition = answers[definition_qid]
                if keyword:
                    Keyword.objects.create(word=keyword, definition=definition, note=hit_object.note, unreviewed=True)
            except KeyError:
                pass

        if assignments:
            logger.info('Done processing HIT {0}'.format(hit_object.HITId))
            hit_object.processed = True
            hit_object.save()


EMAIL_HIT_TITLE_TEMPLATE = 'Identify fields in an email'
EMAIL_HIT_DESCRIPTION = "Read an email about a college course and pull out information " \
                        "about that course."
EMAIL_HIT_OVERVIEW_TEMPLATE = \
        '<p>KarmaNotes.org is a non-profit organization dedicated to free and open education. ' \
        'We receive emails from students with their course notes attached. The bodies of the emails ' \
        'usually describe the course that the notes are about, as well as the notes themselves. ' \
        'We need your help to convert this into a format ' \
        'our system can understand. See the email printed below, and fill out as much information ' \
        'about the course as you are able. You may need to look at the documents attached to the email, ' \
        'which are linked to below it.</p> ' \
        '<p>Subject: {subject}</p> ' \
        '<pre>{body}</pre>'
EMAIL_HIT_ATTACHMENT_OVERVIEW_TEMPLATE = '<p>The follow document was attached to the email. View it and fill out \
                                         as much information as you can about it. <a href="{link}">{name}</a></p>'
EMAIL_HIT_KEYWORDS = 'email, copying, reading, writing'
EMAIL_HIT_DURATION = 60 * 60 * 24 * 7
EMAIL_HIT_REWARD = 0.10
EMAIL_HIT_PERCENT_APPROVED_REQUIREMENT = PercentAssignmentsApprovedRequirement(comparator='GreaterThan', integer_value=95)
EMAIL_HIT_QUALIFICATION = Qualifications(requirements=[KEYWORDS_HIT_PERCENT_APPROVED_REQUIREMENT])

COURSE_NAME_QID = 'course_name'
INSTRUCTOR_NAMES_QID = 'instructor_names'
SCHOOL_NAME_QID = 'school_name'
DEPARTMENT_NAME_QID = 'department_name'
CATEGORY_QID = 'category'
TAGS_QID = 'tags'
NOTE_CATEGORIES_FOR_MTURK = [(c[1], c[0]) for c in Document.NOTE_CATEGORIES]

FP_POLICY_JSON_READ_WRITE = '{{"expiry": {0}, "call": ["store","read","stat"]}}'
FP_POLICY_JSON_READ_WRITE = FP_POLICY_JSON_READ_WRITE.format(int(time.time() + 31536000))
FP_POLICY_READ_WRITE      = encode_fp_policy(FP_POLICY_JSON_READ_WRITE)
FP_SIGNATURE_READ_WRITE   = sign_fp_policy(FP_POLICY_READ_WRITE)

FP_POLICY_JSON_READ = '{{"expiry": {0}, "call": ["read","stat"]}}'
FP_POLICY_JSON_READ = FP_POLICY_JSON_READ.format(int(time.time() + 31536000))
FP_POLICY_READ      = encode_fp_policy(FP_POLICY_JSON_READ)
FP_SIGNATURE_READ   = sign_fp_policy(FP_POLICY_READ)

CONTENT_DISPOSITION_REGEX = r'filename="(?P<filename>.+)"'


@task(name='check_notes_mailbox')
def check_notes_mailbox():
    try:
        user = os.environ['NOTES_MAILBOX_USERNAME']
        password = os.environ['NOTES_MAILBOX_PASSWORD']
        filepicker_api_key = os.environ['FILEPICKER_API_KEY']
    except:
        logger.warn('Could not find notes mailbox secrets, not running check_notes_mailbox')
        return

    mailbox = poplib.POP3_SSL('pop.gmail.com', 995)
    mailbox.user(user)
    mailbox.pass_(password)
    numMessages = len(mailbox.list()[1])
    for i in range(numMessages):
        # construct message object from raw message
        raw_message_string = '\n'.join(mailbox.retr(i+1)[1])
        message = email.message_from_string(raw_message_string)

        if not message.is_multipart():
            logger.warn('Got an email with no attachments')
            continue

        attachments = []
        message_body = ''

        message_parts = message.get_payload()
        for part in message_parts:
            # Look for the message's plain text body
            if part.get_content_type() == 'text/plain' and part['Content-Disposition'] is None:
                message_body = part.get_payload()

            # Look for attachments
            elif part['Content-Disposition'] and 'attachment;' in part['Content-Disposition']:
                attachment_mimetype = part.get_content_type()
                attachment_filename = re.search(CONTENT_DISPOSITION_REGEX, part['Content-Disposition']).group('filename')

                if part['Content-Transfer-Encoding'] == 'base64':
                    attachment_data = base64.decodestring(part.get_payload())
                else:
                    attachment_data = part.get_payload()

                # Upload attachment to filepicker
                resp = requests.post('https://www.filepicker.io/api/store/S3?key={key}&policy={policy}&' \
                                     'signature={signature}&mimetype={mimetype}&filename={filename}'
                                     .format(key=filepicker_api_key, policy=FP_POLICY_READ_WRITE,
                                             signature=FP_SIGNATURE_READ_WRITE, mimetype=attachment_mimetype,
                                             filename=attachment_filename),
                                      data=attachment_data)

                if resp.status_code == 200:
                    url = json.loads(resp.text)['url']
                    url = url + '?policy={policy}&signature={signature}'\
                        .format(policy=FP_POLICY_READ, signature=FP_SIGNATURE_READ)
                    attachments.append((url, attachment_filename))
                else:
                    logger.warn('Could not upload an attachment to filepicker')

        message_subject = message['Subject']

        overview = Overview()
        overview.append(FormattedContent(
            EMAIL_HIT_OVERVIEW_TEMPLATE.format(subject=message_subject, body=message_body, attachments='')))

        question_form = QuestionForm()
        question_form.append(overview)

        course_name_content = QuestionContent()
        course_name_content.append_field('Title', 'Course Name')
        course_name = Question(identifier=COURSE_NAME_QID,
                               content=course_name_content,
                               answer_spec=AnswerSpecification(FreeTextAnswer()),
                               is_required=True)
        question_form.append(course_name)

        instructor_names_content = QuestionContent()
        instructor_names_content.append_field('Title', 'Instructor Name(s)')
        instructor_names = Question(identifier=INSTRUCTOR_NAMES_QID,
                                    content=instructor_names_content,
                                    answer_spec=AnswerSpecification(FreeTextAnswer()),
                                    is_required=False)
        question_form.append(instructor_names)

        school_name_content = QuestionContent()
        school_name_content.append_field('Title', 'School Name')
        school_name = Question(identifier=SCHOOL_NAME_QID,
                               content=school_name_content,
                               answer_spec=AnswerSpecification(FreeTextAnswer()),
                               is_required=True)
        question_form.append(school_name)

        department_name_content = QuestionContent()
        department_name_content.append_field('Title', 'Department Name')
        department_name = Question(identifier=DEPARTMENT_NAME_QID,
                                   content=department_name_content,
                                   answer_spec=AnswerSpecification(FreeTextAnswer()),
                                   is_required=False)
        question_form.append(department_name)

        for attachment in attachments:
            overview = Overview()
            overview.append(FormattedContent(
                EMAIL_HIT_ATTACHMENT_OVERVIEW_TEMPLATE.format(link=attachment[0], name=attachment[1])))

            category_content = QuestionContent()
            category_content.append_field('Title', 'Note Title')
            category = Question(identifier=NOTE_TITLE_QID,
                                content=category_content,
                                answer_spec=AnswerSpecification(FreeTextAnswer()),
                                is_required=True)
            question_form.append(category)


            category_content = QuestionContent()
            category_content.append_field('Title', 'Note Category')
            answer = SelectionAnswer(style='dropdown', selections=NOTE_CATEGORIES_FOR_MTURK)
            category = Question(identifier=CATEGORY_QID,
                                content=category_content,
                                answer_spec=AnswerSpecification(answer),
                                is_required=True)
            question_form.append(category)


