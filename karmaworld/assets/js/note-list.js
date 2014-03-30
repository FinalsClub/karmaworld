$(function() {
  // load dataTable for course data
  var dataTable = $('#data_table_list').dataTable({
    // we will set column widths explicitly
    'bAutoWidth': false,
    // don't provide a option for the user to change the table page length
    'bLengthChange': false,
    // sepcify the number of rows in a page
    'iDisplayLength': 20,
    // Position the filter bar at the top
    'sDom': dataTable_sDom,
    // Specify options for each column
    "aoColumnDefs": [
      {
        // 2nd element: thanks
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
    'aaSorting': [[1,'desc']]
  });

  if (dataTable.length > 0) {
    // wire up sort chooser
    $('select.note-sort').change(function() {
      dataTable.fnSort([[$(this).val(), 'desc']]);
    });

    // sort by current value of sort chooser, since
    // the browser may change this from our default
    dataTable.fnSort([[$('select.note-sort').val(), 'desc']]);
  }
});
