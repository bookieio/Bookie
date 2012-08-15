<%inherit file="/main_wrap.mako" />
<%def name="title()">Welcome to Bookie</%def>

<div id="welcome" class="yui3-g">
    <div class="yui3-u-1-2">
        <p>Bookie is an open source bookmarking application.</p>
        <p>Host it yourself or feel free to signup for the hosted version.</p>
        <h3>Features</h3>
        <ul>
            <li>Open source!</li>
            <li>Imports from Delicious.com and Google Bookmarks</li>
            <li><a
            href="https://chrome.google.com/webstore/detail/knnbmilfpmbmlglpeemajjkelcbaaega"
            alt="Bookie Chrome Extension">Google Chrome extension</a></li>
            <li>Bookmarklet for other browsers (mobile devices)</li>
            <li>Parse out page content and fulltext search on it</li>
            <li>Support for Sqlite, MySQL, and Postgresql</li>
            <li>Mobile friendly responsive layout</li>
        </ul>

        <h3>Participate</h3>
        <ul>
            <li>
                <a href="/signup" alt="signup for Bookie" title="Signup for Bookie">Signup and test</a>
            </li>
            <li>
                <a href="https://github.com/mitechie/Bookie" title="Bookie on github">Get the source</a>
            </li>
            <li>
                <a href="http://docs.bmark.us" title="Bookie docs">Check out the docs</a>
            </li>
            <li>
                Tip me on Gittip: <br />
                <iframe style="border: 0; margin: 0; padding: 0;"
                    src="https://www.gittip.com/mitechie/widget.html"
                    width="48pt" height="20pt"></iframe>
            </li>
        </ul>

    </div>
    <div class="yui3-u-1-2">
        <div class="form">
            <h2>Signup for Bookie</h2>
            <form id="#signup_form" action="signup_process" method="POST">
                <ul>
                    <li>
                        <label>Email Address</label>
                        <input type="email" id="email" name="email"
                        style="width: 20em;" />
                        <input type="submit" id="send_signup" name="send_signup" value="Sign Up" />
                    </li>
                </ul>
            </form>
        </div>
    </div>
</div>
