
function rescalePdf(viewer) {
  var scaleBase = 750;
  var outlineWidth = 250;
  var frameWidth = parseInt($('#tabs-content')[0].clientWidth);
  var pdfWidth = frameWidth;

  if ($(viewer.sidebar).hasClass('opened')){
    pdfWidth = pdfWidth - 250;
  }

  var newPdfScale = pdfWidth / scaleBase;
  viewer.rescale(newPdfScale);
}

function setupPdfViewer(noteframe, pdfViewer) {

  $('#plus-btn').click(function (){
    pdfViewer.rescale(1.20, true, [0,0]);
  });

  $('#minus-btn').click(function (){
    pdfViewer.rescale(0.80, true, [0,0]);
  });

  // detect if the PDF viewer wants to show an outline
  // at all
  if ($(pdfViewer.sidebar).hasClass('opened')) {
    var body = $(document.body);
    // if the screen is less than 64em wide, hide the outline
    if (parseInt($(body.width()).toEm({scope: body})) < 64) {
      $(pdfViewer.sidebar).removeClass('opened');
    }
  }

  $('#outline-btn').click(function() {
    $(pdfViewer.sidebar).toggleClass('opened');
    // rescale the PDF to fit the available space
    rescalePdf(pdfViewer);
  });

  $('#scroll-to').change(function() {
    page = parseInt($(this).val());
    pdfViewer.scroll_to(page, [0,0]);
  });

  // rescale the PDF to fit the available space
  rescalePdf(pdfViewer);
}

function writeNoteFrame(contents) {
  var dstFrame = document.getElementById('noteframe');
  var dstDoc = dstFrame.contentDocument || dstFrame.contentWindow.document;
  dstDoc.write(contents);
  dstDoc.close();
}

function setupAnnotator(noteElement) {
  noteElement.annotator();
  noteElement.annotator('addPlugin', 'Store', {
    prefix: '/ajax/annotations',
    loadFromSearch: {
      'uri': note_id
    },
    annotationData: {
      'uri': note_id
    }
  });
}

function injectRemoteScript(url, noteframe, onload) {
  var injectScript = noteframe.document.createElement("script");
  injectScript.src = url;
  injectScript.onload = onload;
  noteframe.document.head.appendChild(injectScript);
}

function injectScript(scriptText, noteframe) {
  var injectScript = noteframe.document.createElement("script");
  injectScript.innerHTML = scriptText;
  noteframe.document.body.appendChild(injectScript);
}

function injectRemoteCSS(url, noteframe) {
  var injectCSS = noteframe.document.createElement("link");
  injectCSS.href = url;
  injectCSS.type = 'text/css';
  injectCSS.rel = 'stylesheet';
  noteframe.document.head.appendChild(injectCSS);
}

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

$(function() {

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

  // Embed the converted markdown if it is on the page, else default to the iframe
  if ($('#note-markdown').length > 0) {
    var note_markdown = $('#note-markdown');
    note_markdown.html(marked(note_markdown.data('markdown')));
    setupAnnotator(note_markdown);
  } else {
    $.ajax(note_contents_url, {
      type: 'GET',
      xhrFields: {
        onprogress: function (progress) {
          var percentage = Math.floor((progress.loaded / progress.total) * 100);
          writeNoteFrame("<h3 style='text-align: center'>" + percentage + "%</h3>");
        }
      },
      success: function(data, textStatus, jqXHR) {
        writeNoteFrame(data);

        // run setupAnnotator in frame context
        var noteframe = document.getElementById('noteframe').contentWindow;

        injectRemoteCSS(annotator_css_url, noteframe);
        injectScript("csrf_token = '" + csrf_token + "';", noteframe);

        injectRemoteScript("https://code.jquery.com/jquery-2.1.0.min.js", noteframe,
          function() {
            injectRemoteScript(setup_ajax_url, noteframe);
            injectRemoteScript(annotator_js_url, noteframe,
              function() {
                var js = "$(function() { \
                  var document_selector = $('body'); \
                  if ($('#page-container').length > 0) { \
                    document_selector = $('#page-container'); \
                  } \
                  document_selector.annotator(); \
                  document_selector.annotator('addPlugin', 'Store', { \
                    prefix: '/ajax/annotations', \
                    loadFromSearch: { \
                    'uri': " + note_id + " \
                  }, \
                  annotationData: { \
                    'uri': " + note_id + " \
                  } \
                }); })";
                injectScript(js, noteframe);

                if (pdfControls == true) {
                  var pdfViewer = noteframe.pdf2htmlEX.defaultViewer;
                  $(noteframe.document).ready(function() {
                    setupPdfViewer(noteframe, pdfViewer);
                  });
                }
              });
          });
      },
      error: function(data, textStatus, jqXHR) {
        writeNoteFrame("<h3 style='text-align: center'>Sorry, your note could not be retrieved.</h3>");
      }
    });
  }

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

});


