$(function() {
  $('#flag-button').click(function(event) {
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
        dataType: 'json',
        type: 'POST'
      });
    }
  });

  $('#edit-button').click(function(event) {
    $('#edit-course-form').slideToggle();
  });

  $('#edit-save-btn').click(function(event) {
    $.ajax({
      url: course_edit_url,
      dataType: 'json',
      data: $('#edit-course-form').children().serialize(),
      type: 'POST',
      success: function(data) {
        // We might want to use a template here instead of rehashing logic
        // on both the client and server side
        $('#edit-course-form').slideUp();
        $('.validation_error').remove()
        $('#course_form_errors').text('');
        $('#course_name').text(data.fields.name);
        $('#course_instructor_name').text(data.fields.instructor_name);

        var $externalLinkSquare = $('<i>', {'class': 'fa fa-external-link-square'});
        $('#course_url').text(data.fields.url.slice(0, 50) + ' ');
        $('#course_url').append($externalLinkSquare);
        $('#course_url').attr('href', data.fields.url);
        if (data.fields.url === '') {
          $('#course_link').parent().hide();
        } else {
          $('#course_link').parent().show();
        }
      },
      error: function(resp) {
        var json = JSON.parse(resp.responseText);
        var errors = json.errors;

        // Delete all errors that currently exist
        $('.validation_error').remove()

        // Failed responses with no errors -> display message
        if (!errors) {
          $('#course_form_errors').text(json.message);
        } else {
          if (errors.instructor_email) {
            $.each(errors.instructor_email, function(index, value) {
              $('#id_instructor_email').parent().children('legend').append($('<span>', { class: 'validation_error', text: value }));
            });
          }

          if (errors.url) {
            $.each(errors.url, function(index, value) {
              $('#id_url').parent().children('legend').append($('<span>', { class: 'validation_error' , text: value }));
            });
          }
        }
      }
    });
  });

  KARMAWORLD.Course.initCourseNameAutocomplete({});
  KARMAWORLD.Course.initInstructorNameAutocomplete({});

});
