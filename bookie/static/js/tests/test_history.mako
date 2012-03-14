<html>
<head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <script src="../build/y/yui/yui.js"></script>
    <script src="../bookie/history.js"></script>
    <script src="test_history.js"></script>
    <title>History Tests</title>
</head>
<body class="yui3-skin-sam">

    <script type="text/javascript">
        YUI().use('console', 'test', 'bookie-test-history', function (Y) {
            // RUN ALL THE TESTS!!!!!
            var yconsole = new Y.Console({
                newestOnTop: false
            });
            yconsole.render('#log');

            Y.Test.Runner.add(Y.bookie.test.history.suite);
            Y.Test.Runner.run();
        });
    </script>
</body>
</html>
