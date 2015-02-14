function tabHandler(event) {
  // check for:
  // key pressed was TAB
  // key was pressed in last row
  if (event.which == 9) {
    var totalForms = parseInt($('#id_form-TOTAL_FORMS').attr('value'));
    var formIndex = parseInt($(this).closest('div.keyword-form-row').data('index'));
    if (formIndex === totalForms-1) {
      addForm(event);
      event.preventDefault();
    }
  }
}

function addForm(event) {
  var prototypeForm = $('#keyword-form-prototype div.keyword-form-row').clone().appendTo('#keyword-form-rows');
  var newForm = $('.keyword-form-row:last');
  var totalForms = $('#id_form-TOTAL_FORMS').attr('value');
  var newIdRoot = 'id_form-' + totalForms + '-';
  var newNameRoot = 'form-' + totalForms + '-';

  newForm.data('index', totalForms);

  var keywordInput = newForm.find('.keyword');
  keywordInput.attr('id', newIdRoot + 'keyword');
  keywordInput.attr('name', newNameRoot + 'keyword');
  keywordInput.focus();

  var definitionInput = newForm.find('.definition');
  definitionInput.attr('id', newIdRoot + 'definition');
  definitionInput.attr('name', newNameRoot + 'definition');
  definitionInput.keydown(tabHandler);

  var objectIdInput = newForm.find('.object-id');
  objectIdInput.attr('id', newIdRoot + 'id');
  objectIdInput.attr('name', newNameRoot + 'id');

  $('#id_form-TOTAL_FORMS').attr('value', parseInt(totalForms)+1);

  keywordInput.focus();
}

/**
 * Scale the html given by the selector by the factor.
 * @param {string|jQuery|dom} container - Selector to scale
 * @param {Number} factorDelta - Amount to change the current scaling factor by
 * (e.g. 1.1, 0.9, 2.0).
 */
function scaleHTML(container, factorDelta) {
  var el = $(container);
  var currentFactor = parseFloat(el.attr("data-scale-factor") || 1);
  var factor = currentFactor * factorDelta;
  
  var parent = el.parent()
  var origHeight = parent.height() / currentFactor;
  var destHeight = origHeight * factor;
  // Set the new parent height
  parent.height(destHeight);

  el.attr("data-scale-factor", factor);
  var matrix = "matrix(" + factor + ", 0, 0, " + factor + ", " +
                       "0," + ((destHeight - origHeight) * 0.5) + ")";
  el.css("-webkit-transform", matrix);
  el.css("-moz-transform", matrix);
  el.css("-ms-transform", matrix);
  el.css("transform", matrix);
}

function initNoteContentPage() {

  $("#thank-button").click(function(event) {
    event.preventDefault();

    // increment number in page right away
    var thankNumber = $("#thank-number");
    thankNumber.text(parseInt(thankNumber.text()) + 1);

    // disable thank button so it can't
    // be pressed again
    $(this).hide();
    $('#thank-button-disabled').show();
    $(this).unbind('click');

    // tell server that somebody thanked
    // this note
    $.ajax({
      url: note_thank_url,
      dataType: "json",
      type: 'POST'
    });
  });

  $("#flag-button").click(function(event) {
    event.preventDefault();

    if (confirm('Do you wish to flag this note for deletion?')) {
      // disable thank button so it can't
      // be pressed again
      $(this).hide();
      $('#flag-button-disabled').show();
      $(this).unbind('click');

      // tell server that somebody flagged
      // this note
      $.ajax({
        url: note_flag_url,
        dataType: "json",
        type: 'POST'
      });
    }
  });

  $('#save_note_tags').click(function(event) {
    $.ajax({
      url: edit_note_tags_url,
      dataType: 'json',
      data: $('#note_tags_input').val(),
      type: 'POST',
      success: function(data) {
        $('#note_tags_form').slideUp();
        $('.tags').empty();
        $.each(data.fields.tags, function(index, tag) {
          $('.tags').append($('<span>', { class: 'tag-span', text: tag }));
        });
        $('#note-tag-dialog').foundation('reveal', 'close');
      }
    });
  });

  $("#note-download-button").click(function(event) {
    if (confirm('It costs 2 karma points to download a note. Are you sure?')) {
      // disable handler so it won't be run again
      $(this).unbind('click');

      // tell server that somebody downloaded
      // this note
      $.ajax({
        url: note_downloaded_url,
        dataType: "json",
        type: 'POST',
        async: false
      })
    };
  });

  $('#delete-note-button').click(function (event) {
    if (!confirm("Are you sure you want to delete this note?")) {
      event.preventDefault();
    }
  });

  $("#note-html").annotator({
    readOnly: false
  }).annotator('addPlugin', 'Store', {
    prefix: '/ajax/annotations',
    loadFromSearch: { 'uri': note_id },
    annotationData: { 'uri': note_id }
  });

  $("#plus-btn").click(function() { scaleHTML("#note-html", 1.1); });
  $("#minus-btn").click(function() { scaleHTML("#note-html", 1 / 1.1); });
}

function initNoteKeywordsPage() {
  $('.definition').keydown(tabHandler);
  $('#add-row-btn').click(addForm);

  $('#keywords-data-table').dataTable({
    // don't provide a option for the user to change the table page length
    'bLengthChange': false,
    'sDom': 't<"clear">'
  });

  $('#edit-keywords-button').click(function(event) {
    $('#keywords-data-table').toggle();
    $('#keyword-form').toggle();
  });

}

function markQuestionCorrect(question) {
  question.find('.quiz-question').addClass('correct');
  question.find('.quiz-question').removeClass('incorrect');
  question.find('.correct-label').show();
  question.find('.incorrect-label').hide();
}

function markQuestionIncorrect(question) {
  question.find('.quiz-question').addClass('incorrect');
  question.find('.quiz-question').removeClass('correct');
  question.find('.incorrect-label').show();
  question.find('.correct-label').hide();
}

function initQuizPage() {
  $('#check-answers-button').click(function() {
    $('.quiz-question-wrapper').each(function() {
      var choice = $(this).find('input:checked');
      if (choice.length) {
        if (choice.data('correct') == true) {
          markQuestionCorrect($(this));
        } else {
          markQuestionIncorrect($(this));
        }
      }


      var options_selected = $(this).find('option:selected');
      if (options_selected.length > 0) {
        var matching_correct = true;
        options_selected.each(function() {
          if ($(this).data('correct') == false) {
            matching_correct = false;
          }
        });
        if (matching_correct) {
          markQuestionCorrect($(this));
        } else {
          markQuestionIncorrect($(this));
        }
      }
    });
  });
}

