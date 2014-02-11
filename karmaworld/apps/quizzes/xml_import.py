from StringIO import StringIO
import re
from bs4 import BeautifulSoup
from karmaworld.apps.quizzes.models import MultipleChoiceQuestion, Quiz, TrueFalseQuestion, MultipleChoiceOption
from pyth.plugins.plaintext.writer import PlaintextWriter
from pyth.plugins.rtf15.reader import Rtf15Reader

FOUR_MULTIPLE_CHOICE = r'^A. (?P<A>.*)[\n]+B. (?P<B>.*)[\n]+C. (?P<C>.*)[\n]+D. (?P<D>.*)$'
TRUE_FALSE_CHOICE = r'^A. (?P<A>True|False)[\n]+B. (?P<B>True|False)$'


def _rtf2plain(str):
    if str:
        doc = Rtf15Reader.read(StringIO(str))
        return PlaintextWriter.write(doc).getvalue()
    else:
        return str


def _category_from_question(question):
    category_string = question.find('Category').string
    if category_string == 'Knowledge':
        category = MultipleChoiceQuestion.KNOWLEDGE
    elif category_string == 'Understand':
        category = MultipleChoiceQuestion.UNDERSTAND
    elif category_string == 'Remember':
        category = MultipleChoiceQuestion.REMEMBER
    elif category_string == 'Analyze':
        category = MultipleChoiceQuestion.ANALYZE
    else:
        category = None

    return category


def _difficulty_from_question(question):
    difficulty_string = question.find('Difficulty').string
    if difficulty_string == 'Easy':
        difficulty = MultipleChoiceQuestion.EASY
    elif difficulty_string == 'Medium':
        difficulty = MultipleChoiceQuestion.MEDIUM
    elif difficulty_string == 'Hard':
        difficulty = MultipleChoiceQuestion.HARD
    else:
        difficulty = None

    return difficulty


def _true_false(question, quiz_object):
    question_text = _rtf2plain(question.find('QuestionText').string)
    explanation_text = _rtf2plain(question.find('Explanation').string)
    category = _category_from_question(question)
    difficulty = _difficulty_from_question(question)

    correct_answer_letter = question.find('Answer').string

    options_string = question.find('AnswerOptions').string
    options_string = _rtf2plain(options_string)
    match_options = re.match(TRUE_FALSE_CHOICE, options_string)
    option_a = match_options.group('A')
    option_b = match_options.group('B')

    if correct_answer_letter == 'A':
        correct_answer_string = option_a
    else:
        correct_answer_string = option_b

    if correct_answer_string == 'True':
        correct_answer = True
    else:
        correct_answer = False

    TrueFalseQuestion.objects.create(text=question_text,
                                     explanation=explanation_text,
                                     difficulty=difficulty,
                                     category=category,
                                     true=correct_answer,
                                     quiz=quiz_object)


def _multiple_choice(question, quiz_object):
    question_text = _rtf2plain(question.find('QuestionText').string)
    explanation_text = _rtf2plain(question.find('Explanation').string)
    category = _category_from_question(question)
    difficulty = _difficulty_from_question(question)

    question_object = MultipleChoiceQuestion.objects.create(question_text=question_text,
                                                            explanation=explanation_text,
                                                            difficulty=difficulty,
                                                            category=category,
                                                            quiz=quiz_object)

    correct_answer = question.find('Answer').string

    options_string = question.find('AnswerOptions').string
    options_string = _rtf2plain(options_string)
    match_options = re.match(FOUR_MULTIPLE_CHOICE, options_string)
    option_a = match_options.group('A')
    option_b = match_options.group('B')
    option_c = match_options.group('C')
    option_d = match_options.group('D')

    MultipleChoiceOption.objects.create(text=option_a,
                                        correct=(correct_answer == 'A'),
                                        question=question_object)
    MultipleChoiceOption.objects.create(text=option_b,
                                        correct=(correct_answer == 'B'),
                                        question=question_object)
    MultipleChoiceOption.objects.create(text=option_c,
                                        correct=(correct_answer == 'C'),
                                        question=question_object)
    MultipleChoiceOption.objects.create(text=option_d,
                                        correct=(correct_answer == 'D'),
                                        question=question_object)


def quiz_from_xml(filename):
    with open(filename, 'r') as file:
        soup = BeautifulSoup(file.read(), "xml")

    quiz_name = soup.find('EChapterTitle').string
    quiz_object = Quiz.objects.create(name=quiz_name)

    questions = soup.find_all('TestBank')
    for question in questions:
        type_string = question.find('Type').string
        if type_string == 'Multiple Choice':
            _multiple_choice(question, quiz_object)

        elif type_string == 'True/False':
            _true_false(question, quiz_object)
