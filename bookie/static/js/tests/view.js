// Create a new YUI instance and populate it with the required modules.
YUI({
    logInclude: { TestRunner: true},
    filter: 'raw'
}).use('console', 'test', 'bookie-view', 'bookie-model', function (Y) {
    //initialize the console
    var yconsole = new Y.Console({
        newestOnTop: false
    });
    yconsole.render('#log'),
    bookmark = {

    },
    bmarklist = [
        {
            "username": "admin",
            "updated": "",
            "extended": "",
            "description": "Nuclear Crisis: NRC Says Spent Fuel Pool at Unit 4 Lost Massive Amounts of Water; Japan Disputes Claims",
            "tags": [], "url": "http://feeds.abcnews.com/click.phdo?i=578f79c4656ec416ce71fab58f31fb5b",
            "bid": 11, "total_clicks": 0, "stored": "2011-03-16 20:18:12",
            "inserted_by": "importer",
            "tag_str": "",
            "clicks": 0, "hash_id": "eeead0f74ff680"},
        {
            "username": "admin",
            "updated": "",
            "extended": "",
            "description": "Oh, Ubisoft: Torrented Their Own Music?",
            "tags": [], "url": "http://feedproxy.google.com/~r/RockPaperShotgun/~3/iYGzlyjrIuM/",
            "bid": 12, "total_clicks": 0, "stored": "2011-03-16 08:00:13",
            "inserted_by": "importer",
            "tag_str": "",
            "clicks": 0, "hash_id": "b1210b874f52a1"},
        {
            "username": "admin",
            "updated": "",
            "extended": "RT @shiflett: Can we get rid of Flash yet?",
            "description": "Security Advisory for Adobe Flash Player, Adobe Reader and Acrobat (APSA11-01) \u00c2\u00ab  Adobe Product Security Incident Response Team (PSIRT) Blog",
            "tags": [], "url": "http://blogs.adobe.com/psirt/2011/03/security-advisory-for-adobe-flash-player-adobe-reader-and-acrobat-apsa11-01.html",
            "bid": 13, "total_clicks": 0, "stored": "2011-03-15 21:49:58",
            "inserted_by": "importer",
            "tag_str": "",
            "clicks": 0, "hash_id": "b0e35b6d2fc562"},
        {
            "username": "admin",
            "updated": "",
            "extended": "",
            "description": "Software Carpentry \u00c2\u00bb Literate Programming",
            "tags": [], "url": "http://software-carpentry.org/2011/03/4069/",
            "bid": 14, "total_clicks": 0, "stored": "2011-03-15 18:19:38",
            "inserted_by": "importer",
            "tag_str": "",
            "clicks": 0, "hash_id": "c70694d2c53494"},
        {
            "username": "admin",
            "updated": "",
            "extended": "RT @davewiner: Adjix automatically saves your links to your S3 bucket when they are created. Every web service should do this.  ...",
            "description": "(500) http://r2",
            "tags": [], "url": "http://r2",
            "bid": 15, "total_clicks": 0, "stored": "2011-03-15 17:39:56",
            "inserted_by": "importer",
            "tag_str": "",
            "clicks": 0, "hash_id": "af0b78fb818196"},
        ];


    var view_test = new Y.Test.Case({
        name: "View Tests",

        setUp: function () {
        },


        tearDown: function () {
            Y.one('.view').setContent('');
        },

        testViewExists: function () {
            Y.Assert.isObject(Y.bookie.BmarkView,
                              "Should find an objcet for Bmark view");
        },

        test_render_view: function () {
            var model = new Y.bookie.Bmark(bmarklist[0]),
                testview = new Y.bookie.BmarkView({model: model});

            Y.one('.view').appendChild(testview.render());

            Y.Assert.isTrue(
                Y.one('.view').get('innerHTML').search("eeead0f74ff680") !== -1,
                'We should find the hash id in the rendered html'
            );
        },

        test_render_list: function () {
            var models = new Y.bookie.BmarkList();
            models.add(Y.Array.map(
                bmarklist, function (bmark){
                    return new Y.bookie.Bmark(bmark);
                })
            );

            models.each(function (m, i) {
                var testview = new Y.bookie.BmarkView({model: m});
                Y.one('.view').appendChild(testview.render());
            });

            Y.Assert.isTrue(
                Y.one('.view').get('innerHTML').search("c70694d2c53494") !== -1,
                'We should find the hash id of a middle bmark in the html'
            );
        }
    });

    Y.Test.Runner.add(view_test);
    Y.Test.Runner.run();
});
