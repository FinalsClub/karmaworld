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

  $('#edit-course-form').dialog({
    autoOpen: false,
    modal: true,
    show: { effect: 'fade', duration: 500 },
    width: dialogWidth
  });

  $('#edit-button').click(function(event) {
    $('#edit-course-form').dialog("open");
  });

  $('#edit-save-btn').click(function(event) {
    $.ajax({
      url: course_edit_url,
      dataType: 'json',
      data: $('#edit-course-form').children().serialize(),
      type: 'POST',
      success: function(data) {
        if (data.fields.new_url) {
          window.location.href = data.fields.new_url;
        }

        // We might want to use a template here instead of rehashing logic
        // on both the client and server side
        $('#edit-course-form').slideUp();
        $('.validation_error').remove()
        $('#course_form_errors').empty();
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
        var json;
        try {
          json = JSON.parse(resp.responseText);
        } catch(e) {
          json = { message: 'Unknown Error' };
        }

        var errors = json.errors;

        // Delete all errors that currently exist
        $('.validation_error').remove()
        $('#course_form_errors').empty();

        // Failed responses with no errors -> display message
        if (!errors) {
          $('#course_form_errors').text(json.message);
        } else {
          // Ugly, be works.  Could look into backbone or something similar to make it cleaner.
          if (errors.__all__) {
            $.each(errors.__all__, function(index, value) {
              $('#course_form_errors').append($('<span>', { class: 'validation_error', text: value }));
            });
          }

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

  $('#data_table_list').dataTable({
    // remove the default filter label
    'oLanguage': {
      'sSearch': '',
    },
    // we will set column widths explicitly
    'bAutoWidth': false,
    // don't provide a option for the user to change the table page length
    'bLengthChange': false,
    // sepcify the number of rows in a page
    'iDisplayLength': 20,
    // Position the filter bar at the top
    // DIFF: do not show search bar (f)
    'sDom': '<"top">rt<"bottom"p><"clear">',
    // Specify options for each column
    "aoColumnDefs": [
      {
        // 3rd element: likes
        "aTargets": [ 2 ],
        "bSortable": true,
        "bVisible": true,
        "mData": function ( source, type, val ) {
          //console.log(source);
          if (type === 'set') {
            source.count = val;
            // Store the computed dislay and filter values for efficiency
            // DIFF: label name change.
            source.count_display = val=="" ? "" : "<span>"+val+" Thanks</span>";
            return;
          }
          else if (type === 'display') {
            return source.count_display;
          }
          // 'sort', 'type', 'filter' and undefined all just use the integer
          return source.count;
        }
      },
      {
        // 2nd element: date
        "aTargets": [ 1 ],
        "bSortable": true,
        "bVisible": true,
        "mData": function ( source, type, val ) {
          //console.log(source);
          if (type === 'set') {
            source.date = val;
            // DIFF: label name change.
            source.date_display = val=="" ? "" : "<span>Uploaded "+val+"</span>";
            return;
          }
          else if (type === 'display') {
            return source.date_display;
          }
          // for types 'sort', 'type', 'filter' and undefined use raw date
          return source.date;
        }
      },
      {
        // 1st element: "sort by" label
        "aTargets": [ 0 ],
        "bSortable": false,
        "bVisible": true
      }
    ],
    // Initial sorting
    'aaSorting': [[2,'desc']]
  });

});
