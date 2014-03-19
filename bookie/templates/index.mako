<%inherit file="/main_wrap.mako" />
<%def name="title()">Welcome to Bookie</%def>

<div id="welcome" class="" style="max-width: 1000px;">
    <div class="signup">
        <div class="form">
            <h2>Enter Email to Signup</h2>
            <form id="#signup_form" action="signup_process" method="POST">
                <ul>
                    <li>
                        <input type="email" id="email" name="email"
                        placeholder="email address" />
                        <input type="submit" id="send_signup" name="send_signup" value="Sign Up" />
                    </li>
                </ul>
            </form>
        </div>
    </div>

    <div class="">
        <p>Bookie is an open source bookmarking application.</p>
        <p>Host it yourself or feel free to signup for the hosted version.</p>
        <div>Features</div>
        <ul class="features">
            <li>Open source!</li>
            <li>Imports from Delicious.com, Google Bookmarks, Chrome, and
                Firefox</li>
            <li><a
            href="https://chrome.google.com/webstore/detail/knnbmilfpmbmlglpeemajjkelcbaaega"
            alt="Chrome Extension">Google Chrome extension</a></li>
            <li><a
            href="https://addons.mozilla.org/en-US/firefox/addon/bookie/"
            alt="Firefox Extension">Firefox extension</a></li>

            <li>Bookmarklet for other browsers (mobile devices)</li>
            <li>Parse web page content and fulltext search on it</li>
            <li>Mobile friendly responsive layout</li>
        </ul>

        <div>Participate</div>
        <ul class="features">
            <li>
                <a href="https://github.com/mitechie/Bookie" title="Bookie on github">Get the source</a>
            </li>
            <li>
                <a href="http://docs.bmark.us" title="Bookie docs">Check out the docs</a>
            </li>
            <li>
                <a href="https://groups.google.com/forum/#!forum/bookie_bookmarks">Join the mailing list</a>
            </li>
        </ul>

        <p>
            <a href="https://github.com/mitechie" title="Gittip for mitechie">
            Tip me on Gittip </a>
        </p>
        <iframe style="border: 0; margin: 0; padding: 0;"
            src="https://www.gittip.com/mitechie/widget.html"
            width="48pt" height="20pt"></iframe>
    </div>
</div>
