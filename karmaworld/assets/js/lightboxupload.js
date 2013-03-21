$(function(){

  // Show the 'add note' form
  // first, instantiate the fileuploader on page load
  // TODO: connect it to the '^ save' form submit
  // Show the upload lightbox on upload button click

  $('#add-note-btn').click(function(){
    // TODO: rewrite to .show the form with a slide transition
    $('#add-note-form').show();
    $('input#file_upload_input').click();
  });

  // Submit the add-note form
  $('#save-btn').click(function(){
    $('#add-note-form').submit();
  });

  // Dismiss x click
  $(".lightbox_close").click(function() {
    $(".modal_content").hide();
  });

  var uploader = new qq.FileUploader( {
      action: ajax_upload_url, // added to page via template var
      element: $('#file-uploader')[0],
      multiple: false,
      onComplete: function( id, fileName, responseJSON ) {
        if( responseJSON.success ) {
          //console.log( "success!" ) ;
          $('form#upload_form').attr('action', responseJSON.note_url);
          $('input.submit_upload').show();
        }
      },
      onAllComplete: function( uploads ) {
        // uploads is an array of maps
        // the maps look like this: { file: FileObject, response: JSONServerResponse }
        console.log( "All complete!" ) ;
        // TODO: set a success state
      },
      onProgress: function(id, fileName, loaded, total) {
        console.log("running onProgress " + fileName + " " + loaded);
        console.log(String((100*loaded/total)+'%'));
        $('#progress-fill').animate({
          width: String((100*loaded/total)+'%')}, 5000);
      },
      params: {
        'csrf_token': csrf_token,
        'csrf_name': 'csrfmiddlewaretoken',
        'csrf_xname': 'X-CSRFToken',
        'course_id': courseId, // added to page via template var
      },
    }) ;
});
