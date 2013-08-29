<%inherit file="/main_wrap.mako" />
<%namespace file="../accounts/func.mako" import="password_reset"/>
<%def name="title()">Activate your account</%def>
<%include file="../jstpl.mako"/>

${password_reset(user, reset=True)}
