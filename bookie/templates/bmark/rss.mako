<%

	import time

	app_url = request.route_url('home').rstrip('/')
	time_format = '%Y-%m-%d %H:%M:%S'

%><%def name="rss_title()"><%
	rss_title = 'Latest bookmarks'
	if username:
		rss_title += ' from ' + username
	if tags:
		rss_title += ' tagged with ' + ", ".join(tags)
%>${rss_title}</%def><?xml version="1.0"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
	<channel>
		<title>Bookie: ${rss_title()}</title>
		<link>${app_url}</link>
		<atom:link href="${request.current_route_url()}" rel="self" type="application/rss+xml" />
		<description>bookmark your web</description>
		% for bmark in bmarks:
		<item>
			<title><![CDATA[${bmark['description']}]]></title>
			<description><![CDATA[${bmark['extended']}]]></description>
			<%
				local_timestamp = time.mktime(time.strptime(bmark['stored'], time_format))
				gmt_date_string = time.strftime('%a, %d %b %Y %H:%M:%S', time.gmtime(local_timestamp))
			%><pubDate>${gmt_date_string} GMT</pubDate>
			<link>${app_url}/redirect/${bmark['hash_id']}</link>
			<guid isPermaLink="false">${app_url}#${bmark['bid']}</guid>
			% for tag in bmark['tags']:
			<category>${tag['name']}</category>
			% endfor
		</item>
		% endfor
	</channel>
</rss>