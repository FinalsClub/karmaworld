

function showQuestion() {
  $('div.question').hide();
  $('div[data-question-index="' + current_question_index + '"]').show();
}

function nextQuestion() {
  if (current_question_index+1 < num_quiz_questions) {
    current_question_index += 1;
    showQuestion();
  }
}

function prevQuestion() {
  if (current_question_index-1 >= 0) {
    current_question_index -= 1;
    showQuestion();
  }
}

function checkAnswerCallback(data, textStatus, jqXHR) {
  var question = $('div[data-question-index="' + current_question_index + '"]');
  var question_text = question.find('p.question-text');
  if (data.correct == true) {
    question_text.removeClass('wrong-answer');
    question_text.removeClass('correct-answer');
    question_text.addClass('correct-answer-flash');
    question_text.switchClass('correct-answer-flash', 'correct-answer',1000);
  }
  if (data.correct == false) {
    question_text.removeClass('wrong-answer');
    question_text.removeClass('correct-answer');
    question_text.addClass('wrong-answer-flash');
    question_text.switchClass('wrong-answer-flash', 'wrong-answer',1000);
  }
}

function checkAnswer() {
  var question = $('div[data-question-index="' + current_question_index + '"]');
  var question_id = question.attr('data-question-id');
  var question_type = question.attr('data-question-type');

  var chosen_answer = null;

  if (question_type == 'MultipleChoiceQuestion') {
    var checked = question.find('input:checked');
    if (checked.length == 1) {
      chosen_answer = checked[0].getAttribute('data-choice-id');
    }
  }

  else if (question_type == 'FlashCardQuestion') {
    chosen_answer = question.find('input').val();
  }

  else if (question_type == 'TrueFalseQuestion') {
    var checked = question.find('input:checked');
    if (checked.attr('value') == 'true') {
      chosen_answer = true;
    }
    else if (checked.attr('value') == 'false') {
     chosen_answer = false;
    }
  }

  message = {
    question_type: question_type,
    id: question_id,
    answer: chosen_answer
  };
  $.post(check_answer_url, message, checkAnswerCallback);
}

$(function () {
  showQuestion();
  $('button.check-answer').click(checkAnswer);
  $('button.prev-question').click(prevQuestion);
  $('button.next-question').click(nextQuestion);
});