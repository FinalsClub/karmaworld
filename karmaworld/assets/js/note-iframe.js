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
      //alert('height: ' + newheight);
  }

