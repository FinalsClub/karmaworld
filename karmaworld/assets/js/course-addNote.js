if(window.location.hash) {

  // Get the first hasgh, remove the # character
  var hash = window.location.hash.substring(1); 
  if (hash === 'add-note'){
  	alert('Adding a note!');
  }
}
