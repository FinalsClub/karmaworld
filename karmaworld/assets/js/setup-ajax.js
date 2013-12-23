function setupAjax(){
  // Assumes variable csrf_token is made available
  // by embedding document
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
        // Only send the token to relative URLs i.e. locally.
        xhr.setRequestHeader("X-CSRFToken", csrf_token);
        console.log("preparing request to " + settings.url);
      }
    }
  });
}

$(function() {
  setupAjax();
});