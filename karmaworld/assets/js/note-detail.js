// resize the iframe based on internal contents on page load
function autoResize(id){
  var newheight;
  var newwidth;

  if(document.getElementById){
    newheight = document.getElementById(id).contentWindow.document .body.scrollHeight;
    newwidth = document.getElementById(id).contentWindow.document .body.scrollWidth;
  }

  document.getElementById(id).height = (newheight + 10) + "px";
  document.getElementById(id).width= (newwidth + 5) + "px";
}

function setupPdfViewer() {
  var pdfViewer = document.getElementById("noteframe").contentWindow.pdf2htmlEX.defaultViewer;

  $('#plus-btn').click(function (){
    pdfViewer.rescale(1.20, true, [0,0]);
  });

  $('#minus-btn').click(function (){
    pdfViewer.rescale(0.80, true, [0,0]);
  });

  if ($(pdfViewer.sidebar).hasClass('opened')) {
    // only show outline on large screens
    var body = $('body');
    if (parseInt($(body.width()).toEm({scope: body})) < 64) {
      $(pdfViewer.sidebar).removeClass('opened');
    }
  }

  $('#outline-btn').click(function() {
    $(pdfViewer.sidebar).toggleClass('opened');
  });

  $('#scroll-to').change(function() {
    page = parseInt($(this).val());
    pdfViewer.scroll_to(page, [0,0]);
  });
}

$(function() {
  $("#thank-button").click(function() {
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
});
