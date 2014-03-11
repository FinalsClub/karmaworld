window.KARMAWORLD = window.KARMAWORLD ||  {};
window.KARMAWORLD.Course = {
  initCourseNameAutocomplete: function(autocompleteOpts) {
    var opts = $.extend( {}, autocompleteOpts, {
      source: function(request, response){
        var school_id = $('#id_school').val();
        $.ajax({
          url: json_school_course_list,
          data: {q: request.term, school_id: school_id},
          success: function(data) {
            if (data['status'] === 'success') {
              response($.map(data['courses'], function(item) {
                return {
                    value: item.name,
                    label: item.name,
                };
              }));
            }
          },
          dataType: "json",
          type: 'POST'
        });
      },
      minLength: 3
    });
    $("#id_name").autocomplete(opts);
  },

  initInstructorNameAutocomplete: function(autocompleteOpts) {
    var opts = $.extend( {}, autocompleteOpts, {
      source: function(request, response) {
        var school_id = $('#id_school').val();
        var course_name = $('#id_name').val();
        $.ajax({
          url: json_school_course_instructor_list,
          data: {q: request.term, school_id: school_id, course_name: course_name},
          success: function(data) {
            if (data['status'] === 'success') {
              // Fill in the autocomplete entries
              response($.map(data['instructors'], function(item) {
                return {
                    value: item.name,
                    label: item.name,
                    url:   item.url
                };
              }));
            }
          },
          dataType: "json",
          type: 'POST'
        });
      },
      minLength: 3
    });

    $("#id_instructor_name").autocomplete(opts);
  }
};

function dialogWidth() {
  var bodyWidth = $('body').width();
  if (bodyWidth < 700) {
    return bodyWidth;
  } else {
    return 700;
  }
}
