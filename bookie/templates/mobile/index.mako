<%inherit file="/mobile_wrap.mako" />
<%def name="title()">Bookie Bookmarks</%def>
<%def name="header()">

    <style type="text/css">
        .head {
            background: #CCCCCC;
            border-bottom: 2px solid #333;
            color: #363d52;
            font-family: 'Cabin Sketch',arial,helvetica,clean,sans-serif;
            text-shadow: 4px 4px 4px #CCCCCC;
        }

        .footer {
            border-top: 2px solid #333;
            background: #CCCCCC;
            color: #363d52;
        }

        .footer a.ui-link {
            color: #363d52;
            text-decoration: none;
        }

        .head h1.ui-title {
        }
    </style>


</%def>

<div data-role="page">

    <header data-role="header" class="head">
        <span style="float: left"><img src="/static/images/logo.16.png" alt="Bookie"/></span>
        <span style="float: right; padding-top: .2em;">
            <a href="/search" data-role="button" data-icon="search" data-theme="a"
            data-iconpos="right">Search</a>&nbsp;
        </span>
        <h1>Bookie</h1>
    </header>

    <div data-role="content">
       <p>Here's some body stuff for you</p>
    </div>

    <footer data-role="footer" class="footer" data-position="fixed">
        &nbsp;
        <!--<h4><a href="${request.route_url('mobile')}">Home</a></h4>-->
    </footer>

</div>
