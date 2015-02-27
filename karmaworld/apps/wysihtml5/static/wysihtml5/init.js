function initWysihtml5(element) {
  var editor = new wysihtml5.Editor(element, {
    toolbar: element.id + "-toolbar",
    parserRules: wysihtml5ParserRules
  });
  return editor;
}
