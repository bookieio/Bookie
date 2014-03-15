YUI().use('bookie-model', 'bookie-view', function(Y) {
    var options = new Y.bookie.OptionsModel();
    options.load(onOptionsLoad);
    function onOptionsLoad() {
        var view = new Y.bookie.OptionsView({
            model: options
        });
        view.render();
    }
});