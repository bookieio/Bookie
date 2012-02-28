<%
    date_fmt = "%m/%d/%Y"
    combo = request.registry.settings['combo_server']
%>
<html>
    <head>
        <meta http-equiv="X-UA-Compatible" content="IE=8" />
        <meta name="viewport" content="width=device-width" initial-scale="1.0">
        <title>Bookie: ${self.title()}</title>
        <script type="text/javascript"
        src="${combo}/combo?y/yui/yui-min.js&b/meta.js&y/loader/loader-min.js&y/substitute/substitute-min.js"></script>

        <link rel="stylesheet" type="text/css"
        href="${combo}/combo?y/cssreset/reset-min.css&y/cssfonts/cssfonts-min.css&y/cssgrids/cssgrids-min.css&y/cssbase/cssbase-min.css&y/widget-base/assets/skins/sam/widget-base.css&y/autocomplete-list/assets/skins/sam/autocomplete-list.css"/>
        <link
            href='https://fonts.googleapis.com/css?family=Cabin|Cabin+Sketch:bold&v2'
            rel='stylesheet' type='text/css'/>
        <link rel="stylesheet" type="text/css" href="/static/css/responsive.css"/>
        <script type="text/javascript">
            YUI.GlobalConfig = {
                combine: true,
                base: '${combo}/combo?y/',
                comboBase: '${combo}/combo?',
                maxURLLength: 1500,
                root: 'y/',
                groups: {
                    bookie: {
                        combine: true,
                        base: '${combo}/combo?b',
                        comboBase: '${combo}/combo?',
                        root: 'b/',
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
                <span class="item"><a href="/recent" class="button nav_button">All</a></span>

                % if request.user:
                    <span class="item"><a href="/${request.user.username}/recent" class="button nav_button">Mine</a></span>
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

        <%namespace file="deployfunc.mako" import="installspecific"/>
        ${installspecific()|n}
    </body>
</html>

