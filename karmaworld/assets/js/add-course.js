// Setup all the javascript stuff we need for the various
// incarnations of the Add Course form
$(function() {

  // Set up the "Add Course" button at bottom
  // of page
  $('#add-course-btn').click(function() {
    // Show the add a course form
    $('#add-course-form').show();
    // Hide the add a course button
    $('#add-course-btn').hide();
    // Put focus in first input field
    $('#str_school').focus();
  });

  // Set up the "Add Course" button in the
  // page header
  $('#add_course_header_button').click(function() {
    // Show the add a course form
    $('#add-course-form').show();
    // Hide the add a course button
    $('#add-course-btn').hide();
    // Scroll the user's page to here
    $('#add-course-divider').ScrollTo();
    // Put focus in first input field
    $('#str_school').focus();
  });

  // Dismiss on exit x click FIXME
  $(".lightbox_close").click(function() {
    $(".modal_content").hide();
  });

  function setupAjax(){
    // Assumes variable csrf_token is made available
    // by embedding document
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
          // Only send the token to relative URLs i.e. locally.
          xhr.setRequestHeader("X-CSRFToken", csrf_token);
        }
      }
    });
  }

  setupAjax();

  $("#str_school").autocomplete({
    source: function(request, response){
      $.ajax({
        url: json_school_list,
        data: {q: request.term},
        success: function(data) {
          console.log(data);
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
      console.log("select func");
      console.log("id");
      console.log(ui.item.value);
      console.log("name");
      console.log(ui.item.label);
      // don't let the user edit the field anymore
      //$('#str_school').attr('readonly', true);

      // set the school id as the value of the hidden field
      $('#id_school').val(ui.item.real_value);
      // set the School name as the textbox field
      //$('#str_school').val(ui.item.label);
    },
    minLength: 3
  });

  $("#id_name").autocomplete({
    source: function(request, response){
      var school_id = $('#id_school').val()
      $.ajax({
        url: json_school_course_list,
        data: {q: request.term, school_id: school_id},
        success: function(data) {
          console.log(data);
          if (data['status'] === 'success') {
            response($.map(data['courses'], function(item) {
              return {
                  value: item.name,
                  label: item.name,
              };
            }));
          } else {
            // FIXME: do something?
          }
        },
        dataType: "json",
        type: 'POST'
      });
    },
    minLength: 3
  });


});
