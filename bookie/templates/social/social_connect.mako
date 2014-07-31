<!DOCTYPE html>

<html>
<title>Bookie - Connecting...</title>

<head>
    <meta name="viewport" content="initial-scale=1, maximum-scale=1">
    
        <link
            href='https://fonts.googleapis.com/css?family=Cabin|Cabin+Sketch:bold&v2'
            rel='stylesheet' type='text/css'/>
        <link rel="stylesheet" type="text/css" href="/static/css/responsive.css"/>    

        <script type="text/javascript" charset="utf-8">
        %if url:
        <!-- If Credentials are not present in the URL this timeout redirects to twitter oauth url to recieve users oauth details -->
            var next = "${url}";
            setTimeout(function() {
                console.log(["Forwarding to next", next]);
                window.location.href = next;
            }, 1000); 
        %else:
        <!-- Once Credentials are received this timeout redirects to settings page closing the windows-->
            setTimeout(function() {
                console.log("${result}");
                window.close();
                window.location.href = "${request.route_url('user_account', username=request.user.username)}";
            }, 2000);
        %endif
    </script>
</head>

<body>

    <div style="text-align: center;">
        %if result:
            <h2>${result}</h2>
            %if retry_link:
            <a href="${request.route_url('twitter_connect')}">Click Here</a>
            %endif
        %else:
            <img src="/static/images/play_store_512.png" style="padding: 0 5px;" alt="Bookie Extensions"/>    
            <div>Hold on just a sec...</div>
        %endif

    </div>

</body>
</html>

