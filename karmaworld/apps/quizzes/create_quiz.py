import random
from karmaworld.apps.notes.models import Note
from karmaworld.apps.quizzes.models import MultipleChoiceQuestion, Quiz, TrueFalseQuestion, MultipleChoiceOption, \
    Keyword, FlashCardQuestion

KEYWORD_MULTIPLE_CHOICE = 1
DEFINITION_MULTIPLE_CHOICE = 2
KEYWORD_DEFINITION_TRUE_FALSE = 3
FLASHCARD_KEYWORD_BLANK = 4
GENERATED_QUESTION_TYPE = (
    KEYWORD_MULTIPLE_CHOICE,
    DEFINITION_MULTIPLE_CHOICE,
    KEYWORD_DEFINITION_TRUE_FALSE,
    FLASHCARD_KEYWORD_BLANK,
)

MULTIPLE_CHOICE_CHOICES = 4


def _create_keyword_multiple_choice(keyword, keywords, quiz):
    question_object = MultipleChoiceQuestion.objects.create(
        question_text=keyword.definition,
        quiz=quiz)

    MultipleChoiceOption.objects.create(
        text=keyword.word,
        correct=True,
        question=question_object)

    for other_keyword in random.sample(keywords.exclude(id=keyword.id), MULTIPLE_CHOICE_CHOICES - 1):
        MultipleChoiceOption.objects.create(
            text=other_keyword.word,
            correct=False,
            question=question_object)


def _create_definition_multiple_choice(keyword, keywords, quiz):
    question_object = MultipleChoiceQuestion.objects.create(
        question_text=keyword.word,
        quiz=quiz)

    MultipleChoiceOption.objects.create(
        text=keyword.definition,
        correct=True,
        question=question_object)

    for other_keyword in random.sample(keywords.exclude(id=keyword.id), MULTIPLE_CHOICE_CHOICES - 1):
        MultipleChoiceOption.objects.create(
            text=other_keyword.definition,
            correct=False,
            question=question_object)


def _create_keyword_definition_true_false(keyword, keywords, quiz):
    true = random.choice((True, False))

    if true:
        definition = keyword.definition
    else:
        other_keyword = keywords.exclude(id=keyword.id)
        definition = other_keyword.definition

    question_text = 'Is the following a correct definition of {w}:<br/>{d}'. \
        format(w=keyword.word, d=definition)

    TrueFalseQuestion.objects.create(
        text=question_text,
        quiz=quiz,
        true=true)


def _create_keyword_flashcard_blank(keyword, quiz):
    FlashCardQuestion.objects.create(
        definition_side=keyword.definition,
        keyword_side=keyword.word,
        quiz=quiz)


def quiz_from_keywords(note_id):
    note_object = Note.objects.get(id=note_id)
    quiz_object = Quiz.objects.create(note=note_object, name=note_object.name)
    keywords = Keyword.objects.filter(note=note_object)

    for keyword in keywords:
        if keyword.word and keyword.definition:
            question_type = random.choice(GENERATED_QUESTION_TYPE)

            if question_type is KEYWORD_MULTIPLE_CHOICE:
                _create_keyword_multiple_choice(keyword, keywords, quiz_object)

            elif question_type is DEFINITION_MULTIPLE_CHOICE:
                _create_definition_multiple_choice(keyword, keywords, quiz_object)

            elif question_type is KEYWORD_DEFINITION_TRUE_FALSE:
                _create_keyword_definition_true_false(keyword, keywords, quiz_object)

            elif question_type is FLASHCARD_KEYWORD_BLANK:
                _create_keyword_flashcard_blank(keyword, quiz_object)


