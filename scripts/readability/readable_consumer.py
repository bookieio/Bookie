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

def post_readable(hash_id, content):
    """Send off the parsing request to the web server"""
    url = 'http://127.0.0.1:6543/api/v1/bmarks/readable'

    data = urllib.urlencode({'hash_id': hash_id,
                             'content': content.encode('utf-8')})

    try:
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        res = response.read()
        assert "true" in str(res)
    except Exception, exc:
        print "FAILED: " + hash_id
        print str(exc)

bean.watch('default')

while True:
    job = bean.reserve()
    j = json.loads(urllib.unquote(job.body))

    if 'hash_id' in j and 'content' in j:
        print j['hash_id']
        post_readable(j['hash_id'], j['content'])
    else:
        print "ERROR: missing fields -- " + j['hash_id']
    job.delete()

