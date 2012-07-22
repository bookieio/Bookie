YUI().use('bookie-chrome', function (Y) {
    var b = new Y.bookie.chrome.BackgroundPage();
    b.init_background();
});

window.inject_readable = function (callback) {
    chrome.tabs.executeScript(null, {file:"readable.js"});
};
