<%inherit file="/main_wrap.mako" />
<%def name="title()">Sign up for Bookie!</%def>
<div class="form">
    <p>
        <a href="" id="signup_heading" class="heading">
            <span aria-hidden="true" class="icon icon-envelope" title="Sign up for Bookie"></span>
            <em class="icon">Sign Up</em>
            Sign up for Bookie!
        </a>
    </p>
    <div id="signup_body">
	<p>Bookie is currently in alpha.</p>

        % if message:
            <p id="signup_msg" class="success">${message}</p>
        % else:
            <p>If you'd like to have an account please submit your email address
            and we'll send you an email in our next wave of sign ups.</p>
            <form id="#signup_form" action="signup_process" method="POST">
                <ul>
                    <li>
                        <label>Email Address</label>
                        <input type="email" id="email" name="email" />
                        <input type="submit" id="send_signup" name="send_signup" value="Sign Up" />
                    </li>
                </ul>
            </form>
        %endif
    </div>
    % if errors:
        <div id="signup_msg" class="error">${errors['email']}</div>
    % endif
</div>
