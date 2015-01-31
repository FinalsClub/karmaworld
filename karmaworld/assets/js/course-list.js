$(function() {

  function tableRow(courseData) {
    var rowContents = $('#data-table-entry-prototype').clone();
    rowContents.find('.data-table-entry').removeClass('hide');
    rowContents.find('.table-school').text(courseData['school']);
    rowContents.find('.table-department').text(courseData['department']);
    rowContents.find('.table-instructor').text(courseData['instructor']);
    rowContents.find('.table-course-name').text(courseData['name']);
    rowContents.find('.table-course-link').attr('href', courseData['link']);
    rowContents.find('.file-count').text(courseData['file_count']);
    rowContents.find('.thanks-count').text(courseData['popularity']);
    rowContents.find('.updated-at').text(courseData['updated_at']);
    return rowContents.html();
  }

  // load dataTable for course data
  var dataTable = $('#data_table_list').dataTable({
    // we will set column widths explicitly
    'autoWidth': false,
    // don't provide a option for the user to change the table page length
    'lengthChange': false,
    // sepcify the number of rows in a page
    'displayLength': 20,
    // Position the filter bar at the top
    'dom': '<"top">rt<"bottom"p><"clear">',
    // Initial sorting
    'aaSorting': [[2,'desc']],
    'paging': true,
    'columns': [
      { 'name': 'course', 'orderable': false, 'searchable': true, 'visible': true,
        'class': 'small-12 columns data-table-entry-wrapper' },
      { 'name': 'date', 'orderable': true, 'searchable': false, 'visible': false },
      { 'name': 'note_count', 'orderable': true, 'searchable': false, 'visible': false },
      { 'name': 'popularity', 'orderable': true, 'searchable': false, 'visible': false }
    ],
    'createdRow': function(row, data, index) {
      $(row).addClass('table-row');
    },
    // Use server-side processing
    'processing': true,
    'serverSide': true,
    'ajax': function(data, callback, settings) {
        $.get(course_list_ajax_url, data, function(dataWrapper, textStatus, jqXHR) {
          for (i = 0; i < dataWrapper.data.length; i++) {
            dataWrapper.data[i][0] = tableRow(dataWrapper.data[i][0]);
          }
          callback(dataWrapper);
        });
    }
  });

  // wire up search box
  $('#search-courses').keyup(function() {
    dataTable.fnFilter($(this).val());
  });

  // wire up sort chooser
  $('#sort-by').change(function() {
    var sortCol = $(this).val();
    dataTable.fnSort([[sortCol, 'desc']]);
  });

  // sort by current value of sort chooser, since
  // the browser may change this from our default
  var sortCol = $('#sort-by').val();
  dataTable.fnSort([[sortCol, 'desc']]);

  // filter by chosen school
  $('#school-filter').change(function() {
    var schoolName = $(this).val();
    if (schoolName === 'ALL') {
      dataTable.fnFilter('');
    } else {
      dataTable.fnFilter(schoolName);
    }
  });

  // ensure that upon reload, any previous selection is used
  // (make a reload look like a change for triggering the above code)
  $('#school-filter').trigger('change');

});

