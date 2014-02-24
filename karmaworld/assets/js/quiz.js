
function tabHandler(event) {
  // check for:
  // key pressed was TAB
  // key was pressed in last row
  if (event.which == 9 &&
      (!$(this).closest('div.keyword-form-row').next().hasClass('keyword-form-row'))) {
    addForm(event);
  }
}

function addForm(event) {
  var prototypeForm = $('#keyword-form-prototype div.keyword-form-row').clone().appendTo('#keyword-form-rows');
  var newForm = $('.keyword-form-row:last');
  var totalForms = $('#id_form-TOTAL_FORMS').attr('value');
  var newIdRoot = 'id_form-' + totalForms + '-';
  var newNameRoot = 'form-' + totalForms + '-';

  var keywordInput = newForm.find('.keyword');
  keywordInput.attr('id', newIdRoot + 'keyword');
  keywordInput.attr('name', newNameRoot + 'keyword');

  var definitionInput = newForm.find('.definition');
  definitionInput.attr('id', newIdRoot + 'definition');
  definitionInput.attr('name', newNameRoot + 'definition');
  definitionInput.keydown(tabHandler);

  var objectIdInput = newForm.find('.object-id');
  objectIdInput.attr('id', newIdRoot + 'id');
  objectIdInput.attr('name', newNameRoot + 'id');

  $('#id_form-TOTAL_FORMS').attr('value', parseInt(totalForms)+1);
}

$(function() {
  $('.definition').keydown(tabHandler);
  $('#add-row-btn').click(addForm);
});

