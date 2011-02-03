<%
    from pylons import app_globals
    from morpylons.lib import auth
    from repoze.what.predicates import not_anonymous, in_group
%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
    <meta http-equiv="X-UA-Compatible" content="IE=8" />
    <title>Quipp: ${self.title()}</title>

    % if hasattr(self, 'header'):
        ${self.header()}
    % endif

    <link rel="stylesheet" type="text/css"
    href="http://yui.yahooapis.com/combo?3.2.0/build/cssreset/reset-min.css&3.2.0/build/cssfonts/fonts-min.css&3.2.0/build/cssgrids/grids-min.css&3.2.0/build/cssbase/base-min.css">
    <link rel="stylesheet" type="text/css" href="http://yui.yahooapis.com/combo?2in3.3/2.8.1/build/yui2-skin-sam-button/assets/skins/sam/yui2-skin-sam-button-min.css&" />
    <link rel="stylesheet" type="text/css" href="http://yui.yahooapis.com/combo?2in3.3/2.8.1/build/yui2-skin-sam-datatable/assets/skins/sam/yui2-skin-sam-datatable-min.css&" />

    ${h.stylesheet_link('/css/quipp.css')}
    <script type="text/javascript"
    src="http://yui.yahooapis.com/combo?3.2.0/build/yui/yui-min.js&3.2.0/build/oop/oop-min.js&3.2.0/build/dom/dom-min.js&3.2.0/build/dom/dom-style-ie-min.js&3.2.0/build/event-custom/event-custom-base-min.js&3.2.0/build/event/event-base-min.js&3.2.0/build/pluginhost/pluginhost-min.js&3.2.0/build/node/node-min.js&3.2.0/build/event/event-delegate-min.js&3.2.0/build/json/json-min.js&3.2.0/build/querystring/querystring-stringify-simple-min.js&3.2.0/build/queue-promote/queue-promote-min.js&3.2.0/build/datatype/datatype-xml-min.js&3.2.0/build/io/io-min.js&3.2.0/build/dom/selector-css3-min.js&3.2.0/build/pluginhost/pluginhost-min.js&3.2.0/build/base/base-min.js&3.2.0/build/editor/editor-min.js"></script>

    <!--<script type="text/javascript">-->
    <!--    YUI().use("node", "yui2-button", "io"); -->
    <!--</script>-->

</head>
<body class="yui-skin-sam">
    <div class="yui3-g">
        <div class="yui3-u-1">
            <div id="mor_message"><div>App messages go here</div></div>

            <div id="header">
                <div id="nav_links">
                    <ul id="navlist">
                        <li>${h.link_to('Home', h.url('/'))}</li>

                        % if hasattr(c, 'current_user') and c.current_user.user_name is not None:
                            % if auth.check(in_group('admin')):
                                <li>${h.link_to('Users', h.url(controller='accounts', action='list'))}</li>
                                <li>${h.link_to('Log', h.url(controller='root', action='activity'))}</li>
                                <li>${h.link_to('Admin', h.url(controller='qcontent', action='admin'))}</li>
                            % endif
                            <li>${h.link_to('Logout', h.url('/logout_handler'))}</li>
                        % else:
                            <li>${h.link_to('Login', h.url('/login'))}</li>
                        % endif
                    </ul>
                </div>
            </div>

            <div id="body">
                ${next.body()}
                <div style="clear: both;">&nbsp;</div>
            </div>

            <div id="footer">
                <div class="right">Quipp:
                    <a href="http://webint.morpace-i.com/sphinx/quipp/changelog.html" title="changelog"><span id="version">$version</span></a>

                </div>
                <div class="left">
                    % if hasattr(c, 'current_user') and c.current_user.user_name is not None:
                        ${c.current_user.user_name}
                    % else:
                        Anon
                    % endif
                </div>
            </div>

            <div id="mor_modal"></div>

            <div id="javascript">

                <script type="text/javascript">
                    YUI().use("node", "yui2-button", "io");
                </script>

                ${h.javascript_link('/js/mor.yui.js')}
                ${h.javascript_link('/js/quipp.js')}

                % if hasattr(self, 'add_js'):
                    ${self.add_js()}
                % endif

            </div>
        </div>
    </div>
</body>
</html>
