
function addForm(event) {

  // check for:
  // key pressed was TAB
  // key was pressed in last row
  if (event.which == 9 &&
      (!$(this).closest('div.keyword-form-row').next().hasClass('keyword-form-row'))) {

    var prototypeFormString = $('#keyword-form-prototype').text();
    var newForm = $('#keyword-form-rows').append(prototypeFormString).find('.keyword-form-row:last');
    var totalForms = $('#id_form-TOTAL_FORMS').attr('value');
    var newIdRoot = 'id_form-' + totalForms + '-';
    var newNameRoot = 'form-' + totalForms + '-';

    var keywordInput = newForm.find('.keyword');
    console.log(newForm);
    console.log(keywordInput);
    keywordInput.attr('id', newIdRoot + 'keyword');
    keywordInput.attr('name', newNameRoot + 'keyword');

    var definitionInput = newForm.find('.definition');
    definitionInput.attr('id', newIdRoot + 'definition');
    definitionInput.attr('name', newNameRoot + 'definition');
    definitionInput.keydown(addForm);

    var objectIdInput = newForm.find('.object-id');
    objectIdInput.attr('id', newIdRoot + 'id');
    objectIdInput.attr('name', newNameRoot + 'id');

    $('#id_form-TOTAL_FORMS').attr('value', parseInt(totalForms)+1);

  }
}

$(function() {
  $('.definition').keydown(addForm);
});

