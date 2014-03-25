

// resize the iframe based on internal contents on page load
function autoResize(id){
  var newheight;
  var newwidth;

  if(document.getElementById){
    newheight = document.getElementById(id).contentWindow.document.body.scrollHeight;
    newwidth = document.getElementById(id).contentWindow.document.body.scrollWidth;
  }

  document.getElementById(id).height = (newheight + 10) + "px";
  document.getElementById(id).width= (newwidth + 5) + "px";
}

function rescalePdf(viewer, frameWidth) {
  var scaleBase = 750;
  var outlineWidth = 250;
  var pdfWidth = frameWidth;

  if ($(viewer.sidebar).hasClass('opened')){
    pdfWidth = pdfWidth - 250;
  }

  var newPdfScale = pdfWidth / scaleBase;
  viewer.rescale(newPdfScale);
}

function setupPdfViewer() {
  var noteFrame = document.getElementById("noteframe")
  var pdfViewer = noteFrame.contentWindow.pdf2htmlEX.defaultViewer;

  $('#plus-btn').click(function (){
    pdfViewer.rescale(1.20, true, [0,0]);
  });

  $('#minus-btn').click(function (){
    pdfViewer.rescale(0.80, true, [0,0]);
  });

  // detect if the PDF viewer wants to show an outline
  // at all
  if ($(pdfViewer.sidebar).hasClass('opened')) {
    var body = $('body');
    // if the screen is less than 64em wide, hide the outline
    if (parseInt($(body.width()).toEm({scope: body})) < 64) {
      $(pdfViewer.sidebar).removeClass('opened');
    }
  }

  $('#outline-btn').click(function() {
    $(pdfViewer.sidebar).toggleClass('opened');
    // rescale the PDF to fit the available space
    rescalePdf(pdfViewer, parseInt(noteFrame.width));
  });

  $('#scroll-to').change(function() {
    page = parseInt($(this).val());
    pdfViewer.scroll_to(page, [0,0]);
  });

  // rescale the PDF to fit the available space
  rescalePdf(pdfViewer, parseInt(noteFrame.width));
}

function writeNoteFrame(contents) {
  var dstFrame = document.getElementById('noteframe');
  var dstDoc = dstFrame.contentDocument || dstFrame.contentWindow.document;
  dstDoc.write(contents);
  dstDoc.close();
}

$(function() {

  $("#tabs").tabs();

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

  $('#note-tag-dialog').dialog({
    title: "Edit note tags",
    autoOpen: false,
    modal: true,
    show: { effect: 'fade', duration: 500 },
    width: dialogWidth()
  });

  $('#edit-note-tags').click(function(event) {
    $('#note-tag-dialog').dialog("open");
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
        $('#note-tag-dialog').dialog("close");
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
    $('#note-markdown').html(marked($('#note-markdown').data('markdown')));
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
        autoResize('noteframe');
        if (pdfControls == true) {
          setupPdfViewer();
        }
      },
      error: function(data, textStatus, jqXHR) {
        writeNoteFrame("<h3 style='text-align: center'>Sorry, your note could not be retrieved.</h3>");
      }
    });
  }



});
