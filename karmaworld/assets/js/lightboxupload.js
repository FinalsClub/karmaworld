$(function(){

  // Show the 'add note' form
  // first, instantiate the fileuploader on page load
  // TODO: connect it to the '^ save' form submit
  // Show the upload lightbox on upload button click

  // check if we arrived at this page planning on uploading a note
  if(window.location.hash) {

    // Get the first hasgh, remove the # character
    var hash = window.location.hash.substring(1);
    if (hash === 'add-note'){

      $('#add-note-form').show();
      $('#file-uploader').show();
      $('div.upload-status').hide();
    }
  }

  $('#add-note-btn').click(function(){
    // show the add note form
    // TODO: rewrite to .show the form with a slide transition
    $('#add-note-form').show();
    // Bring up the file picker automatically
    $('input#file_upload_input').click();
    // hide the add a note button
    $('#add-note-btn').hide()
  });

  // Dismiss x click
  // FIXME:
  $(".lightbox_close").click(function() {
    $(".modal_content").hide();
  });

  var uploader = new qq.FileUploader( {
      action: ajax_upload_url, // added to page via template var
      element: $('#file-uploader')[0],
      multiple: false,

      onSubmit: function (id, fileName) {
        $('#file-uploader').hide();
        $('div.upload-status').show();
      },

      onComplete: function( id, fileName, responseJSON ) {
        if( responseJSON.success ) {
          // activate the form for submitting
          $('form#upload_form').attr('action', responseJSON.note_url);
          // inform the user of success
          $('#add-note-status').text('Uploaded');
          // TODO: activate the save button
          $('#save-btn').removeClass('disabled');
          // add a click handler to submit the add-note form
          $('#save-btn').click(function(){
            $('form#add-note').submit();
          });

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
        // Animate the progress bar
        $('#progress-fill').animate({
          width: String((100*loaded/total)+'%')}, 5000);
        // fill out the filename
        $('#filename').text(fileName);
      },
      params: {
        'csrf_token': csrf_token,
        'csrf_name': 'csrfmiddlewaretoken',
        'csrf_xname': 'X-CSRFToken',
        'course_id': courseId, // added to page via template var
      },
    }) ;
});
