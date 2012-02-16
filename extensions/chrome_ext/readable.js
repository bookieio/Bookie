// Grab the content's html in the body tag and pass that along to the extension
// so we can pass that along to the server for readable parsing
// This is loaded into the background page when we click the popup button
console.log('running readable.js');
body = document.getElementsByTagName('body')[0];
chrome.extension.sendRequest({'id': 'from_readable', 'html' : body.innerHTML});
