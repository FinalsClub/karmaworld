function initWysihtml5(element) {
  var editor = new wysihtml5.Editor(element, {
    toolbar: element.id + "-toolbar",
    parserRules: wysihtml5ParserRules
  });
  editor.on("change", function() { element.value = editor.value; });
  return editor;
}

(function() {
  var elements = document.querySelectorAll("[role='wysihtml5-rich-text']");
  var elementArr = [];
  for (var i = 0; i < elements.length; i++) {
    elementArr.push(elements[i]);
  }
  elementArr.forEach(initWysihtml5);
})();
