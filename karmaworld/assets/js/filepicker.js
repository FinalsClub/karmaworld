
/*
 *  load the file form template and append it to the form container
 *  takes a fileupload event
 */
makeFileForm = function(upFile) {
  var _form = document.getElementById('form-template').cloneNode(deep=true);
  // save the Filename to the form name field
  $(_form.children[0].children[0].children[1]).val(upFile.filename); // replace with upFile name
  _form.style.display = "inline";
  _form.id = null; // clear the unique id
  // save the FP url to the form
  $(_form.children[0].children[3].children[0]).val(upFile.url);
  // save the mimetype to the form
  $(_form.children[0].children[3].children[1]).val(upFile.mimetype);

  document.getElementById('forms_container').appendChild(_form);

  if (document.location.host === 'www.karmanotes.org' ||
    document.location.host === 'karmanotes.org') {
    _gat._getTracker()._trackEvent('upload', 'filepicker file drop');
  }

  $('.remove').on('click', function(e){
      e.stopPropagation();
      $(this).parent().parent().remove();
  });

  $('#save-btn').show();
}

var uploaded_files = new Array();

$(function(){
  // these are obsolete without the drag-drop widget that we removed from the partial above
  // var $dropzone = $('#filepicker_dropzone');
  var $dropzone_result = $('#filepicker_dropzone_result');

  $('#save-btn').on('click', function(e){
    e.stopPropagation();
    $(this).unbind('click');
    $(this).addClass('disabled');

    var saveIcon = $('#save-btn-icon');
    saveIcon.removeClass('fa-save');
    saveIcon.addClass('fa-spinner fa-spin');

    $('#forms_container .inline-form').each(function(i,el){
        var name, tags, fpurl, course;
        name = $(el).find('.intext').val();
        fp_file = $(el).find('.fpurl').val();
        tags = $(el).find('.taggit-tags').val();
        course = $(el).find('.course_id').val();
        csrf = $(el).find('.csrf').val();
        email = $('#id_email').val();
        mimetype = $(el).find('.mimetype').val();

        $.post(upload_post_url, {
          'name': name,
          'fp_file': fp_file,
          'tags': tags,
          'course': course,
          'csrfmiddlewaretoken': csrf,
          'mimetype': mimetype,
          'email': email
        }, function(data){
          if (data === 'success') {
            // For multiple uploads, we may end up clearing and re-
            //  writing this multiple times, but show the same list
            //  each time.
            $('#uploaded_files').empty();
            for (var i=0; i < uploaded_files.length; i++) {
              $('#uploaded_files').append($('<li>', {text: uploaded_files[i]}));
            }
            $('#thank-points').html(uploaded_files.length*5);
            $('#success').show();
            $('#save-btn').hide();
            $('#filepicker_row').hide();
            $('#forms_container .inline-form').remove();
            $('#forms_container').hide();
            if (document.location.host === 'www.karmanotes.org' ||
              document.location.host === 'karmanotes.org') {
              _gat._getTracker()._trackEvent('upload', 'upload form submitted');
            }
            if (user_is_authenicated) {
              setTimeout(function(){
                location.reload(true);
              }, 20000);
            }
          }
        });
        // Add the name we've just uploaded to the list
        uploaded_files.push(name);
    });
  });

});

var got_file = function(event){
  $('#filepicker_dropzone_result').text(event);
  for (var i=0; i < event.fpfiles.length; i++){
    makeFileForm(event.fpfiles[i]);
  }
};
