from copy import copy
import random
from karmaworld.apps.quizzes.models import Keyword


class BaseQuizQuestion(object):

    def question_type(self):
        return self.__class__.__name__


class MultipleChoiceQuestion(BaseQuizQuestion):
    def __init__(self, question_text, choices):
        self.question_text = question_text
        self.choices = choices

    def __unicode__(self):
        return u"Multiple choice: {0}: {1}".format(self.question_text, ", ".join(map(str, self.choices)))

    def __str__(self):
        return unicode(self)

    def __repr__(self):
        return str(self)


class MultipleChoiceOption(object):
    def __init__(self, text, correct):
        self.text = text
        self.correct = correct

    def __unicode__(self):
        return self.text

    def __str__(self):
        return unicode(self)

    def __repr__(self):
        return str(self)


class TrueFalseQuestion(BaseQuizQuestion):
    def __init__(self, question_text, true):
        self.question_text = question_text
        self.true = true

    def __unicode__(self):
        return u"True or false: {0}".format(self.question_text)

    def __str__(self):
        return unicode(self)

    def __repr__(self):
        return str(self)


KEYWORD_MULTIPLE_CHOICE = 1
DEFINITION_MULTIPLE_CHOICE = 2
KEYWORD_DEFINITION_TRUE_FALSE = 3
GENERATED_QUESTION_TYPE = (
    KEYWORD_MULTIPLE_CHOICE,
    DEFINITION_MULTIPLE_CHOICE,
    KEYWORD_DEFINITION_TRUE_FALSE,
)

MULTIPLE_CHOICE_CHOICES = 4


def _create_keyword_multiple_choice(keyword, keywords):
    choices = [MultipleChoiceOption(text=keyword.word, correct=True)]

    for other_keyword in random.sample(keywords.exclude(id=keyword.id), MULTIPLE_CHOICE_CHOICES - 1):
        choices.append(MultipleChoiceOption(
                       text=other_keyword.word,
                       correct=False))

    question_text = u'Pick the keyword to match "{d}"'.format(d=keyword.definition)

    return MultipleChoiceQuestion(question_text, choices)


def _create_definition_multiple_choice(keyword, keywords):
    choices = [MultipleChoiceOption(text=keyword.definition, correct=True)]

    for other_keyword in random.sample(keywords.exclude(id=keyword.id), MULTIPLE_CHOICE_CHOICES - 1):
        choices.append(MultipleChoiceOption(
                       text=other_keyword.definition,
                       correct=False))

    question_text = u'Pick the definition to match "{w}"'.format(w=keyword.word)

    return MultipleChoiceQuestion(question_text, choices)


def _create_keyword_definition_true_false(keyword, keywords):
    true = random.choice((True, False))

    if true:
        definition = keyword.definition
    else:
        other_keyword = random.choice(keywords.exclude(id=keyword.id))
        definition = other_keyword.definition

    question_text = u'The keyword "{w}" matches the definition "{d}"'. \
        format(w=keyword.word, d=definition)

    return TrueFalseQuestion(question_text, true)


def quiz_from_keywords(note):
    keywords = Keyword.objects.filter(note=note).exclude(word__iexact='').exclude(definition__iexact='')
    questions = []

    if len(keywords) < 4:
        return []

    for keyword in keywords:
        if keyword.word and keyword.definition:
            question_type = random.choice(GENERATED_QUESTION_TYPE)

            if question_type is KEYWORD_MULTIPLE_CHOICE:
                questions.append(_create_keyword_multiple_choice(keyword, keywords))

            elif question_type is DEFINITION_MULTIPLE_CHOICE:
                questions.append(_create_definition_multiple_choice(keyword, keywords))

            elif question_type is KEYWORD_DEFINITION_TRUE_FALSE:
                questions.append(_create_keyword_definition_true_false(keyword, keywords))

    return questions


