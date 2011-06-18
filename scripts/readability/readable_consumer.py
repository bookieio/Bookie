import beanstalkc
import json
import urllib
import urllib2

SERVER = '127.0.0.5'
PORT = 11300

# setup connection
bean = beanstalkc.Connection(host="localhost",
                             port=11300,
                             parse_yaml=lambda x: x.split("\n"))

def post_readable(data):
    """Send off the parsing request to the web server"""
    url = 'http://127.0.0.1:6543/api/v1/bmarks/readable'

    if 'content' in data:
        data['content'] = data['content'].encode('utf-8')

    http_data = urllib.urlencode(data)

    try:
        req = urllib2.Request(url, http_data)
        response = urllib2.urlopen(req)
        res = response.read()
        assert "true" in str(res)
    except Exception, exc:
        print "FAILED: " + data['hash_id']
        print str(exc)

bean.watch('default')

while True:
    job = bean.reserve()
    j = json.loads(urllib.unquote(job.body))
    if 'hash_id' in j:
        print j['hash_id']
        post_readable(j)
    else:
        print "ERROR: missing fields -- " + str(j['hash_id'])
    job.delete()

