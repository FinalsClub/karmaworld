$(function(){
  // Show the upload lightbox on upload button click
  $('#upload_button_container').click(function(){
    $('#lightbox_upload').show()
  });
  // Dismiss all lightboxen on exit x click

  $(".lightbox_close").click(function() {
    $(".modal_content").hide();
  });

  var uploader = new qq.FileUploader( {
      action: uploadUrl, // added to page via template var
      element: $('#file-uploader')[0],
      multiple: true,
      onComplete: function( id, fileName, responseJSON ) {
        if( responseJSON.success )
          console.log( "success!" ) ;
          $('form#upload_form').attr('action', responseJSON.note_url);
          $('input.submit_upload').show();
      },
      onAllComplete: function( uploads ) {
        // uploads is an array of maps
        // the maps look like this: { file: FileObject, response: JSONServerResponse }
        console.log( "All complete!" ) ;
      },
      params: {
        'csrf_token': csrf_token,
        'csrf_name': 'csrfmiddlewaretoken',
        'csrf_xname': 'X-CSRFToken',
        'course_id': courseId, // added to page via template var
      },
    }) ;
});
