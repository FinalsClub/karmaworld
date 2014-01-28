// Setup all the javascript stuff we need for the various
// incarnations of the Add Course form

$(function() {

  var schoolSelected = false;
  var courseNameSelected = false;
  var instructorSelected = false;

  function fieldEdited() {
    if (schoolSelected && courseNameSelected && instructorSelected) {
      $('#save-btn').hide();
      $('#save-btn').addClass('disabled');
      $('#existing-course-msg').show();
    } else {
      $('#save-btn').show();
      $('#save-btn').removeClass('disabled');
      $('#existing-course-msg').hide();
    }
  };

  addCourse = function() {
    // Show the add a course form
    $('#add-course-form').show();
    // Hide the add a course button
    $('#add-course-btn').hide();
    // Scroll the user's page to here
    $('#add-course-divider').ScrollTo();
    // Put focus in first input field
    $('#str_school').focus();
  };

  // Set up the "Add Course" button at bottom
  // of page
  $('#add-course-btn').click(addCourse);

  // Set up the "Add Course" button in the
  // page header
  $('#add_course_header_button').click(addCourse);

  $("#str_school").autocomplete({
    source: function(request, response){
      $.ajax({
        url: json_school_list,
        data: {q: request.term},
        success: function(data) {
          if (data['status'] === 'success') {
            response($.map(data['schools'], function(item) {
              return {
                  value: item.name,
                  real_value: item.id,
                  label: item.name,
              };
            }));
          } else {
            // FIXME: do something if school not found
            $('#create_school_link').show();
          }
        },
        dataType: "json",
        type: 'POST'
      });
    },
    select: function(event, ui) {
      // set the school id as the value of the hidden field
      $('#id_school').val(ui.item.real_value);
      schoolSelected = true;
      $('#str_school').removeClass('error');
      $('#save-btn').removeClass('disabled');
      fieldEdited();
    },
    change: function(event, ui) {
      if (ui.item == null) {
        $('#id_school').val('');
        schoolSelected = false;
        $('#str_school').addClass('error');
        $('#save-btn').addClass('disabled');
        fieldEdited();
      }
    },
    minLength: 3
  });

  KARMAWORLD.Course.initCourseNameAutocomplete({
    select: function(event, ui) {
      courseNameSelected = true;
      fieldEdited();
    },
    change: function(event, ui) {
      if (ui.item == null) {
        courseNameSelected = false;
        fieldEdited();
      }
    }
  });

  KARMAWORLD.Course.initInstructorNameAutocomplete({
    select: function(event, ui) {
      instructorSelected = true;
      $('#existing-course-btn').attr('href', ui.item.url);
      fieldEdited();
    },
    change: function(event, ui) {
      if (ui.item == null) {
        instructorSelected = false;
        $('#existing-course-btn').attr('href', '');
        fieldEdited();
      }
    }
  });

});
