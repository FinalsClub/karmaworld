// setup ajax based autocomplete for the school field in the add course lightbox
$(function() {

  function setupAjax(){
    // Assumes variable csrf_token is made available
    // by embedding document
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
        if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
          // Only send the token to relative URLs i.e. locally.
          xhr.setRequestHeader("X-CSRFToken", '{{ csrf_token }}');
        }
      }
    });
  }

  setupAjax();

  $("#str_school").autocomplete({
    source: function(request, response){
      $.ajax({
        url: "{% url 'json_school_list' %}",
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
      // set the school id as the value of the hidden field
      $('#id_school').val(ui.item.real_value);
      // set the School name as the textbox field
      //$('#str_school').val(ui.item.label);
    },
    minLength: 3
  });
});
