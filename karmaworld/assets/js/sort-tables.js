
// configure the jquery.tablesorter plugin to sort and filter the course list
$(function()
{
  // define pager options
  var pagerOptions = {
    // target the pager markup - see the HTML block below
    container: $(".pager"),
    // output string - default is '{page}/{totalPages}'; possible variables: {page}, {totalPages}, {startRow}, {endRow} and {totalRows}
    output: '{startRow} - {endRow} / {filteredRows} ({totalRows})',
    // if true, the table will remain the same height no matter how many records are displayed. The space is made up by an empty
    // table row set to a height to compensate; default is false
    fixedHeight: true,
    // remove rows from the table to speed up the sort of large tables.
    // setting this to false, only hides the non-visible rows; needed if you plan to add/remove rows with the pager enabled.
    removeRows: false,
    // go to page selector - select dropdown that sets the current page
    cssGoto:   '.gotoPage'
  };

  var widgetOptions = {
    // stripe rows. doesn't work with filter plugin
    zebra : [ "odd", "even" ],

    //Resizable widget: If this option is set to false, resized column widths will not be saved.
    //Previous saved values will be restored on page reload.
    resizable: false,

    // If there are child rows in the table (rows with class name from "cssChildRow" option)
    // and this option is true and a match is found anywhere in the child row, then it will make that row
    // visible; default is false
    filter_childRows : false,

    // if true, a filter will be added to the top of each table column;
    // disabled by using -> headers: { 1: { filter: false } } OR add class="filter-false"
    // if you set this to false, make sure you perform a search using the second method below
    filter_columnFilters : true,

    // css class applied to the table row containing the filters & the inputs within that row
    //filter_cssFilter : 'tablesorter-filter',

    // add custom filter functions using this option
    // see the filter widget custom demo for more specifics on how to use this option
    filter_functions : null,

    // if true, filters are collapsed initially, but can be revealed by hovering over the grey bar immediately
    // below the header row. Additionally, tabbing through the document will open the filter row when an input gets focus
    filter_hideFilters : false,

    // Set this option to false to make the searches case sensitive
    filter_ignoreCase : true,

    // jQuery selector string of an element used to reset the filters
    filter_reset : 'button.reset',

    // Delay in milliseconds before the filter widget starts searching; This option prevents searching for
    // every character while typing and should make searching large tables faster.
    filter_searchDelay : 150,

    // Set this option to true to use the filter to find text from the start of the column
    // So typing in "a" will find "albert" but not "frank", both have a's; default is false
    filter_startsWith : false,

    // Filter using parsed content for ALL columns
    // be careful on using this on date columns as the date is parsed and stored as time in seconds
    filter_useParsedData : false,
  };


  // initialise the tablesorter
  $("#data_table_list").tablesorter(
  {
    widgets: ["filter", "zebra"],
    headers: { 3: { filter: false, sorter: true }, 4: { filter: false, sorter: true } },
    widgetOptions: widgetOptions
  });

  $("#data_table_list").tablesorterPager(pagerOptions);
  console.log('Finished initing tablesorterPager');
});
