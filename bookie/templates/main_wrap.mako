<%
    date_fmt = "%m/%d/%Y"
    combo = request.registry.settings['combo_server']
%>
<html>
    <head>
        <meta http-equiv="X-UA-Compatible" content="IE=8" />
        <title>Bookie: ${self.title()}</title>
        <script src="${combo}/combo/?yui/yui/yui-min.js&bookie/meta.js&yui/loader/loader-min.js&yui/substitute/substitute-min.js"></script>
        <link rel="stylesheet" type="text/css" href="/static/css/yui_reset_layout_grids_3.3.0.css">
        <link href='https://fonts.googleapis.com/css?family=Cabin&v2' rel='stylesheet' type='text/css'>
        <link href='https://fonts.googleapis.com/css?family=Cabin+Sketch:bold&text=Bookie' rel='stylesheet' type='text/css'>
        <link rel="stylesheet" type="text/css" href="/static/css/bookie.css">
        <script type="text/javascript"/>
            YUI.GlobalConfig = {
                combine: true,
                base: '${combo}/combo?yui/',
                comboBase: '${combo}/combo?',
                root: 'yui/',
                groups: {
                    bookie: {
                        combine: true,
                        base: '${combo}/combo/?bookie',
                        comboBase: '${combo}/combo/?',
                        root: 'bookie/',
                        // filter: 'raw',
                        // comes from including bookie/meta.js
                        modules: YUI_MODULES,
                    }
                }
            };
        </script>

        % if hasattr(self, 'header'):
            ${self.header()}
        % endif
        <script type="text/javascript" charset="utf-8">
            <%
                app_url = request.route_url('home').rstrip('/')
            %>
            APP_URL = '${app_url}';

        </script>
    </head>

    <body class="yui3-skin-sam">
        <div id="heading" class="">
            <div class="logo">
                <a href="${app_url}" class="logo">Bookie</a>
                <span class="alt_logo">&nbsp;&#45; bookmark your web</span>
            </div>
            <div class="navigation">
                <span class="item"><a href="/recent" class="button nav_button">All Bookmarks</a></span>

                % if request.user:
                    <span class="item"><a href="/${request.user.username}/recent" class="button nav_button">My Bookmarks</a></span>
                % endif

                <span class="item"><a href="/search" class="button nav_button">Search</a></span>

                % if request.user and request.user.username:
                    <span class="item">
                        <a href="${request.route_url('user_account', username=request.user.username)}" class="button nav_button">Account
                    </a></span>
                % else:
                    <span class="item"><a href="/login" class="button nav_button">Login</a></span>
                % endif

                <!--<span class="item">-->

                <!--</span>-->
            </div>
        </div>
        <div id="body">
            <div class="yui3-g">
                <div class="yui3-u-1">
                    ${next.body()}
                </div>
            </div>
        </div>

        <div class="footer">
            <div class="yui3-g">
            <div class="yui3-u-1-4"></div>
            <div class="yui3-u-3-4">
                <div class="right body">
                    <a href="http://docs.bmark.us">Bookie</a> |
                    <a href="http://github.com/mitechie/Bookie/issues">Support</a> |
                    <a href="http://docs.bmark.us/changes.html">Changes</a> |
                    % if False and request.user:
                        <a href="${request.route_url('user_mobile', username=request.user.username) }">Mobile</a>
                    % endif
                </div>
            </div>
        </div>

        % if hasattr(self, 'add_js'):
            ${self.add_js()}
        % endif
    </body>
</html>
