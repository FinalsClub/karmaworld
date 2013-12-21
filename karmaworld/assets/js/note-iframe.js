// resize the iframe based on internal contents on page load
function autoResize(id){
  var newheight;
  var newwidth;

  if(document.getElementById){
    newheight = document.getElementById(id).contentWindow.document .body.scrollHeight;
    newwidth = document.getElementById(id).contentWindow.document .body.scrollWidth;
  }

  document.getElementById(id).height = (newheight+ 10) + "px";
  document.getElementById(id).width= (newwidth + 5) + "px";


  var currFFZoom = 1;
  var currIEZoom = 100;
  var frameBody = $('#noteframe').contents().find('body');

  $('#plus-btn').on('click',function(){
    if ($.browser.mozilla){
      var step = 0.25;
      currFFZoom += step;
      frameBody.css('MozTransform','scale(' + currFFZoom + ')');
    } else {
      var step = 25;
      currIEZoom += step;
      frameBody.css('zoom', ' ' + currIEZoom + '%');
    }
  });

  $('#minus-btn').on('click',function(){
    if ($.browser.mozilla){
      var step = 0.25;
      currFFZoom -= step;
      frameBody.css('MozTransform','scale(' + currFFZoom + ')');
    } else {
      var step = 25;
      currIEZoom -= step;
      frameBody.css('zoom', ' ' + currIEZoom + '%');
    }
  });
}
