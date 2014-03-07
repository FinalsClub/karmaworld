$(function() {

  if (jump_to_form) {
    $("#add-course-form").show();
    $('#add-course-btn').hide();
    document.getElementById('add-course-form').scrollIntoView(true);
  }

  // load dataTable for course data
  var dataTable = $('#data_table_list').dataTable({
    // we will set column widths explicitly
    'bAutoWidth': false,
    // don't provide a option for the user to change the table page length
    'bLengthChange': false,
    // sepcify the number of rows in a page
    'iDisplayLength': 20,
    // Position the filter bar at the top
    'sDom': '<"top">rt<"bottom"p><"clear">',
    // Specify options for each column
    "aoColumnDefs": [
      {
        // 3rd element: thanks
        "aTargets": [ 2 ],
        "bSortable": true,
        "bVisible": true
      },
      {
        // 2nd element: notes
        "aTargets": [ 1 ],
        "bSortable": true,
        "bVisible": true
      },
      {
        // 1st element: date
        "aTargets": [ 0 ],
        "bSortable": true,
        "bVisible": true
      }
    ],
    // Initial sorting
    'aaSorting': [[2,'desc']]
  });

  // wire up search box
  $('input.search-courses').keyup(function() {
    dataTable.fnFilter($(this).val());
  });

  // wire up sort chooser
  $('select.course-sort').change(function() {
    dataTable.fnSort([[$(this).val(), 'desc']]);
  });

  // sort by current value of sort chooser, since
  // the browser may change this from our default
  dataTable.fnSort([[$('select.course-sort').val(), 'desc']]);

});

