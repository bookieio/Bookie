<%inherit file="/main_wrap.mako" />
<%namespace file="../accounts/func.mako" import="password_reset"/>
<%def name="title()">Activate your account</%def>
<%include file="../jstpl.mako"/>

${password_reset(user, reset=True)}

<%def name="add_js()">
    <script type="text/javascript">
        YUI().use('node', 'bookie-view', 'console', function (Y) {
            Y.on('domready', function () {
                var login_view = new Y.bookie.AccountResetView({
                    api_cfg: {
                        url: APP_URL + '/api/v1'
                    }
                });
            });
        });
    </script>
</%def>
