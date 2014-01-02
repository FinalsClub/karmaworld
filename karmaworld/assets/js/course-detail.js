
$(function() {
  $("#flag-button").click(function(event) {
    event.preventDefault();

    if (confirm('Do you wish to flag this course for deletion?')) {
      // disable thank button so it can't
      // be pressed again
      $(this).hide();
      $('#flag-button-disabled').show();
      $(this).unbind('click');

      // tell server that somebody thanked
      // this note
      $.ajax({
        url: course_flag_url,
        dataType: "json",
        type: 'POST'
      });
    }
  });
});
