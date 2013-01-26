$(function(){
  // Show the upload lightbox on upload button click
  $('#upload_button_container').click(function(){
    $('#lightbox_upload').show()
  });
  // Dismiss all lightboxen on exit x click

  $(".lightbox_close").click(function() {
    $(".modal_content").hide();
  });
});
