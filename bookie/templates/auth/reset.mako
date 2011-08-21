<%inherit file="/main_wrap.mako" />
<%namespace file="../accounts/func.mako" import="password_reset"/>
<%def name="title()">Activate your account</%def>

<input type="hidden" id="username" value="${user.username}" />
<input type="hidden" id="code" value="${user.activation.code}" />

${password_reset(reset=True)}

<%def name="add_js()">
    <script type="text/javascript">
        $(document).ready(function() {
            bookie.reset.init();
        });
    </script>
</%def>
