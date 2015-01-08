<%
    date_fmt = "%m/%d/%Y"
    combo = request.registry.settings['combo_server']
    cache_buster = request.registry.settings['combo_cache_id']
    app_url = request.route_url('home').rstrip('/')
    app_path = request.route_path('home').rstrip('/')
%>
<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="X-UA-Compatible" content="IE=8" />
        <meta name="viewport" content="width=device-width initial-scale=1.0">
        <meta name="mobile-web-app-capable" content="yes">
        <link rel="shortcut icon" sizes="196x196" href="${app_path}/static/images/logo.196.png">
        <title>Bookie: ${self.title()}</title>
        <script type="text/javascript"
        src="${combo}/combo?y/yui/yui-min.js&b/meta.js&y/loader/loader-min.js&y/substitute/substitute-min.js"></script>

        <link rel="stylesheet" type="text/css"
        href="${combo}/combo?y/cssreset/reset-min.css&y/cssfonts/cssfonts-min.css&y/cssgrids/cssgrids-min.css&y/cssbase/cssbase-min.css&y/widget-base/assets/skins/sam/widget-base.css&y/autocomplete-list/assets/skins/sam/autocomplete-list.css"/>
        <link
            href='https://fonts.googleapis.com/css?family=Cabin|Cabin+Sketch:bold&v2'
            rel='stylesheet' type='text/css'/>
        <link rel="stylesheet" type="text/css" href="${app_path}/static/css/responsive.css"/>
        <script type="text/javascript">
            YUI.GlobalConfig = {
                combine: true,
                base: '${combo}${cache_buster}/combo?y/',
                comboBase: '${combo}${cache_buster}/combo?',
                maxURLLength: 1300,
                root: 'y/',
                groups: {
                    bookie: {
                        combine: true,
                        base: '${combo}${cache_buster}/combo?b',
                        comboBase: '${combo}${cache_buster}/combo?',
                        root: 'b/',
                        filter: 'raw',
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

            APP_URL = '${app_url}';
            APP_PATH = '${app_path}';

        </script>
    </head>

    <body class="yui3-skin-sam">
        <div id="heading" class="">
            <div class="logo">
                <a href="${app_url}" class="logo">Bookie</a>
                <span class="alt_logo">&nbsp;&#45; bookmark your web</span>
            </div>
            <div class="navigation">
                <span class="item">
                    <a href="${app_path}/recent" class="button nav_button">
                        <span aria-hidden="true" class="icon icon-tags" title="All Bookmarks"></span>
                        <em class="icon">All Bookmarks</em>
                        <span class="text">All</span>
                    </a>
                </span>

                % if request.user:
                    <span class="item">
                        <a href="${app_path}/${request.user.username}/recent" class="button nav_button">
                            <span aria-hidden="true" class="icon icon-tag"
                            title="My Bookmarks"></span>
                            <em class="icon">My Bookmarks</em>
                            <span class="text">Mine</span>
                        </a>
                    </span>
                % endif

                <span class="item">
                    <a href="${app_path}/search" class="button nav_button">
                        <span aria-hidden="true" class="icon icon-search" title="Search"></span>
                        <em class="icon">Search</em>
                        <span class="text">Search</span>
                    </a>
                </span>

                % if request.user and request.user.username:
                    <span class="item">
                        <a href="${request.route_url('user_account', username=request.user.username)}" class="button nav_button">
                            % if request.user.has_invites():
                                <span aria-hidden="true" class="icon icon-envelope" title="You have invites!"></span>
                                <em class="icon">Invite</em>
                            % else:
                                <span aria-hidden="true" class="icon icon-user" title="Account Details"></span>
                                <em class="icon">Account Details</em>

                            % endif
                            <span class="text">${request.user.username}</span>
                    </a></span>
                % else:
                    <span class="item">
                        <a href="${app_path}/login" class="button nav_button">
                            <span aria-hidden="true" class="icon icon-user" title="Login"></span>
                            <em class="icon">Login</em>
                            <span class="text">Login</span>
                        </a>
                    </span>
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
                    <a href="${app_path}/recent?sort=popular">All Popular Bookmarks</a> |
                    % if request.user and request.user.username:
                        <a href="${app_path}/${request.user.username}/recent?sort=popular">My Popular Bookmarks</a> |
                    % endif
                    <a href="http://docs.bmark.us">Bookie</a> |
                    <a href="http://github.com/bookieio/Bookie/issues">Support</a> |
                    <a href="${request.route_url('dashboard')}">Dashboard</a> |
                    <a href="https://github.com/bookieio/Bookie/commits/develop">Changes</a> |
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

