/* 
 * Methods for fetching pasted html before it gets inserted into content
**/

/* Modern event.clipboardData driven approach.
 * Advantage is that it does not have to loose selection or modify dom to catch the data. 
 * IE does not support though.
**/
wysihtml5.dom.getPastedHtml = function(event) {
  var html;
  if (event.clipboardData) {
    if (wysihtml5.lang.array(event.clipboardData.types).contains('text/html')) {
      html = event.clipboardData.getData('text/html');
    } else if (wysihtml5.lang.array(event.clipboardData.types).contains('text/plain')) {
      html = wysihtml5.lang.string(event.clipboardData.getData('text/plain')).escapeHTML(true, true);
    }
  }
  return html;
};

/* Older temprorary contenteditable as paste source catcher method for fallbacks */
wysihtml5.dom.getPastedHtmlWithDiv = function (composer, f) {
  var selBookmark = composer.selection.getBookmark(),
      doc = composer.element.ownerDocument,
      cleanerDiv = doc.createElement('DIV');
  
  doc.body.appendChild(cleanerDiv);

  cleanerDiv.style.width = "1px";
  cleanerDiv.style.height = "1px";
  cleanerDiv.style.overflow = "hidden";

  cleanerDiv.setAttribute('contenteditable', 'true');
  cleanerDiv.focus();

  setTimeout(function () {
    composer.selection.setBookmark(selBookmark);
    f(cleanerDiv.innerHTML);
    cleanerDiv.parentNode.removeChild(cleanerDiv);
  }, 0);
};