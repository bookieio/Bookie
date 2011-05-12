// Grab the content's html in the body tag and pass that along to the extension
// so we can pass that along to the server for readable parsing
body = document.getElementsByTagName('body')[0];
console.log('running readable.js');
chrome.extension.sendRequest({'html' : body.innerHTML});
