// We need to inject a keyboard listener to trigger the extension popup
//
window.addEventListener("keydown", function(event) {
  // Bind to both command (for Mac) and control (for Win/Linux)
  var modifier = event.ctrlKey || event.metaKey;

  // ctrl-alt-d since ctrl-d is bookmark in chrome
  if (modifier && event.altKey && event.keyCode === 68) {
      // fire to popup the extension
      chrome.extension.sendRequest({'url' : true});
  }
}, false);
