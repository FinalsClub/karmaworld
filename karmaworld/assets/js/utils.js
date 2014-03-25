
function dialogWidth() {
  var bodyWidth = $('body').width();
  if (bodyWidth < 700) {
    return bodyWidth;
  } else {
    return 700;
  }
}
